import commonApi from '@/api';
import { DEFAULT_SORT, MODULES, MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS, USER_STATUS } from '@/utils/constant';
import { getCompanyId, getCurrentUser } from '@/utils/handleAuth';
import { useState } from 'react';

const useBilling = () => {
    const [loading, setLoading] = useState(false);
    const [users, setUsers] = useState([]);
    const [totalRecords, setTotalRecords] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [tableLoader, setTableLoader] = useState(true);
    
    const getUserStorage = async (requestSize, search, limit=10, offset=0, sort = '-1', sortby = 'id') => {
        
        try {
            setLoading(true);
            const currentUser = getCurrentUser();
            const companyId = getCompanyId(currentUser);
            
            // const query = {
            //     searchColumns: ['email', 'fname', 'lname'],
            //     search: search,
            //     // invitedBy: companyId,
            //     $or: [
            //         { 'company.id': companyId }, // 'company.id' must be a complete key-value pair
            //         { invitedBy: companyId }
            //     ],
            //     inviteSts: USER_STATUS.ACCEPT
            // };
            const searchColumns = ['email', 'roleCode', 'fname', 'lname'];
                
            const query = {
                $or: [
                    ...searchColumns.map(column => ({
                        [column]: { $regex: search, $options: 'i' }
                    })),
                    { $expr: { $regexMatch: { input: { $concat: ['$fname', ' ', '$lname'] }, regex: search, options: 'i' } } }
                ], 
                'company.id': companyId,
                inviteSts: USER_STATUS.ACCEPT
            };

            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.BILLING,
                common: true,
                data: {
                    options: {
                        offset: offset,
                        limit: limit,
                        sort: {
                            createdAt: DEFAULT_SORT
                        },
                    },
                    query
                },
            });
            setUsers(response.data);
            setTotalRecords(response?.paginator?.itemCount);
            setTotalPages(response?.paginator?.pageCount || 0);
            setTableLoader(false);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    return { 
        getUserStorage, 
        users, 
        loading, 
        totalPages, 
        totalRecords, 
        tableLoader,
    };
};

export default useBilling;
