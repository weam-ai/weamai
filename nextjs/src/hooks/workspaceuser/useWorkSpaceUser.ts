import commonApi from '@/api';
import { DEFAULT_SORT, MODULES, MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';
import Toast from '@/utils/toast';
import { useState } from 'react';

const useWorkSpaceUser = () => {
    const [loading, setLoading] = useState(false);
    const [workspaceMembers, setWorkSpaceMembers] = useState([]);

    const getList = async (id) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.WORKSPACEUSER,
                common: true,
                data: {
                    options: {
                        sort: {
                            createdAt: DEFAULT_SORT
                        },
                        populate: [
                            {
                                path: 'workspaceId',
                                select: '-updatedAt -__v -isActive'
                            }
                        ],
                        pagination: false
                    },
                    query: {
                        teamId:{$exists:false},
                        searchColumns: [SEARCH_AND_FILTER_OPTIONS.USER_EMAIL],
                        search: '',
                        workspaceId: id
                    },
                },
            });
            setWorkSpaceMembers(response.data);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    const removeWorkspaceMember = async (workspaceId, userId,sharedBrains) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.WORKSPACEUSER,
                data: {
                   user_id:userId,
                   sharedBrains:sharedBrains
                },
                parameters:[workspaceId],
                common: true
            })
            Toast(response.message);
        } catch (error) {
            console.error('error: ', error);
        } finally {
            close();
        }
    }

    const addWorkspaceMember = async (workspaceId, companyId, users) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.WORKSPACEUSER,
                data: {
                    workspaceId,
                    companyId,
                    users
                },
                common: true
            })

            Toast(response.message);
            return true;
        } catch (error) {
            console.log('error: ', error);
        } finally {
            close();
        }
    }

    return { workspaceMembers, getList, removeWorkspaceMember, addWorkspaceMember, loading };
};

export default useWorkSpaceUser;
