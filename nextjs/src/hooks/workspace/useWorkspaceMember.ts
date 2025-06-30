import commonApi from '@/api';
import { MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';
import { getCurrentUser } from '@/utils/handleAuth';
import { useState } from 'react';
import { useSelector } from 'react-redux';

const useWorkspaceMember = () => {
    const [assign, setAssign] = useState([]);
    const user = getCurrentUser();
    const selectedWorkSpace = useSelector((store:any) => store.workspacelist.selected);

    const getAssignList = async (searchValue) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.WORKSPACE_USER_COUNT,
                data: {
                    query: {
                        searchColumns: [SEARCH_AND_FILTER_OPTIONS.USER_EMAIL],
                        search: searchValue,
                        companyId: user.company.id,
                        workspaceId: selectedWorkSpace._id
                    }
                }
            });
            setAssign(response.data);
        } catch (error) {
            console.log('error: ', error);
        }
    };

    return {
        assign,
        getAssignList,
    };
};

export default useWorkspaceMember;
