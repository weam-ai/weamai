import commonApi from '@/api';
import { BRAIN_MEMBER_ADDED, DEFAULT_SORT, MODULES, MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';
import Toast from '@/utils/toast';
import { useState } from 'react';

const useBrainUser = () => {
    const [loading, setLoading] = useState(false);
    const [brainMembers, setBrainMembers] = useState([]);
    
    const getList = async (id) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.SHARE_LIST,
                data: {
                    options: {
                        sort: {
                            createdAt: DEFAULT_SORT
                        },
                        pagination: false
                    },
                    query: {
                        searchColumns: [SEARCH_AND_FILTER_OPTIONS.USER_EMAIL],
                        search: '',
                        'brain.id': id,
                        teamId: { $exists: false },
                    },
                },
            });
            setBrainMembers(response.data);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    const removeBrainMember = async (id, userId) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.UNSHARE,
                data: {
                   user_id:userId
                },
                parameters:[id]
            })
            Toast(response.message);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            close();
        }
    }

    const addBrainMember = async (id, users, workspaceId) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.UPDATE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.BRAINS,
                common: true,
                data: {
                    shareWith:users,
                    isShare:true,
                    workspaceId: workspaceId
                },
                parameters:[id]
            })
            if(response?.code != "ERROR"){
                Toast(response.message);
                return true;
            }else if(response?.code == "ERROR"){
               return false;
            }
        } catch (error) {
            console.log('error: ', error);
        } finally {
            close();
        }
    }

    return { brainMembers, getList, removeBrainMember, addBrainMember, loading };
};

export default useBrainUser;
