'use client';
import commonApi from '@/api';
import { setCreditInfoAction } from '@/lib/slices/chat/chatSlice';
import { setMCPDataAction } from '@/lib/slices/mcpSlice';
import { UserMemberList } from '@/types/user';
import { removeObjectFromArray } from '@/utils/common';
import { DEFAULT_SORT, MODULES, MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';
import { getCompanyId, getCurrentUser, setUserData } from '@/utils/handleAuth';
import { encryptedPersist } from '@/utils/helper';
import { USER } from '@/utils/localstorage';
import Toast from '@/utils/toast';
import { useState } from 'react';
import { useDispatch } from 'react-redux';

const useUsers = () => {
    const [loading, setLoading] = useState(false);
    const [users, setUsers] = useState<UserMemberList[]>([]);
    const [totalRecords, setTotalRecords] = useState(0);
    const [totalInvitation, setTotalInvitation] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [tableLoader, setTableLoader] = useState(true);
    const [loggedInUser,setLoggedInUser]=useState(null)
    const dispatch = useDispatch();
    const getUsersList = async (status , requestSize, search, limit=10, offset=0, sort = '-1', sortby = 'id',isPagination=true,member=true) => {
        try {
            setLoading(true);
            const currentUser = getCurrentUser();
            const companyId = getCompanyId(currentUser); 
            const searchColumns = ['email', 'roleCode', 'fname', 'lname'];
                
            const query:any = {
                $or: [
                    ...searchColumns.map(column => ({
                        [column]: { $regex: search, $options: 'i' }
                    })),
                    { $expr: { $regexMatch: { input: { $concat: ['$fname', ' ', '$lname'] }, regex: search, options: 'i' } } }
                ], 
                'company.id': companyId
                // $or: [ 
                //     { 'company.id': companyId }, // 'company.id' must be a complete key-value pair
                //     { invitedBy: companyId }
                // ]
            };

            if(status != ''){
                query.inviteSts = Array.isArray(status) ? { $in: status } : { $eq: status }
            }
        
            if (requestSize) {
                query.requestSize = { $exists: true };
            }

            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.USER,
                common: true,
                data: {
                    options: {
                        ...(isPagination && { offset: offset, limit: limit }),
                        sort: {
                            createdAt: DEFAULT_SORT,
                        },
                    },
                    query,
                },
            });
            setUsers(response.data);
            member ? setTotalRecords(response?.paginator?.itemCount || 0) : setTotalInvitation(response?.paginator?.itemCount || 0);
            setTotalPages(response?.paginator?.pageCount);
            setTableLoader(false);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    const removeUser = async (userId) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.USER,
                parameters:[userId],
                common: true
            })
            Toast(response.message);
            const updatedObj = removeObjectFromArray(users, userId);
            setUsers(updatedObj);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            close();
        }
    }

    const toggleBrain = async (userIds,toggleStatus,isAll) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.TOGGLE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.USER,
                data:{
                    ...(isAll? {} :{userIds}),
                    toggleStatus
                },
                common:true
            });

             Toast(response.message);
        } catch (error) {
            console.error(`Error in toggleBrain ::: ${error}`);
        }
    };

    const getUserById = async (userId) =>{
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.GET,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.USER,
                parameters:[userId],
                common:true
            });
            encryptedPersist(setUserData(response.data),USER)
            setLoggedInUser(response.data)
            dispatch(setCreditInfoAction(response.data.isFreeTrial));
            dispatch(setMCPDataAction(response.data.mcpdata));     
        } catch (error) {
            console.error(`Error in getUserById ::: ${error}`)
        }
    }

    return { getUsersList, users, loading, totalPages, totalRecords, totalInvitation, removeUser, tableLoader,toggleBrain,getUserById,loggedInUser, setUsers };
};

export default useUsers;
