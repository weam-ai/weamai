import commonApi from '@/api';
import { DEFAULT_SORT, MODULES, MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS, USER_STATUS } from '@/utils/constant';
import { getCompanyId, getCurrentUser } from '@/utils/handleAuth';
import { useState,useEffect } from 'react';

const useMembers = () => {
    const [loading, setLoading] = useState(false);
    const [members, setMembers] = useState([]);
    const user = getCurrentUser(); 
    const companyId = getCompanyId(user); 

    const getMembersList = async (query:any) => {
        try {
            setLoading(true);
            
            const searchColumns = ['email', 'roleCode', 'fname', 'lname'];
            const search = query?.search;
            
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.MEMBERS,
                common: true,
                data: {
                    options: {
                        sort: {
                            createdAt: DEFAULT_SORT
                        },
                        pagination: false
                    },
                    query: {
                        searchColumns: searchColumns,
                        // invitedBy: companyId,
                        'company.id': companyId,
                        // $or: [
                        //     { 'company.id': companyId }, // 'company.id' must be a complete key-value pair
                        //     { invitedBy: companyId }
                        // ],
                        inviteSts: USER_STATUS.ACCEPT,
                        email: { $ne: user?.email },
                        teamId:{$exists:false},
                        ...query
                    },
                },
            });
            setMembers(response.data);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    return { getMembersList, members, loading };
};

export default useMembers;
