import commonApi from '@/api';
import {
    addWorkspaceListAction,
    editWorkspaceListAction,
    setArchiveWorkSpace,
    setWorkSpaceListAction,
} from '@/lib/slices/workspace/workspacelist';
import { workspaceTeamSchema } from '@/schema/team';
import { addMemberWorkSpaceKeys, addWorkSpaceKeys } from '@/schema/workspace';
import { removeObjectFromArray } from '@/utils/common';
import {
    DEFAULT_SORT,
    GENERAL_BRAIN_TITLE,
    MODULES,
    MODULE_ACTIONS,
    SEARCH_AND_FILTER_OPTIONS,
    USER_STATUS,
} from '@/utils/constant';
import { getCompanyId, getCurrentUser } from '@/utils/handleAuth';
import { decryptedPersist, encryptedPersist } from '@/utils/helper';
import { WORKSPACE } from '@/utils/localstorage';
import Toast from '@/utils/toast';
import { yupResolver } from '@hookform/resolvers/yup';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useDispatch, useSelector } from 'react-redux';
import useBrains from '../brains/useBrains';
const defaultValue:any = {
    members: [],
    role: '',
    teamsInput: [],
};
const useWorkspace = ({ addMember, addTeam = false }:any) => {
    const [users, setUsers] = useState([]);
    const [isEdit, setIsEdit] = useState(false);
    const user = getCurrentUser();
    const dispatch = useDispatch();
    const workspacelist = useSelector((store:any) => store.workspacelist.list);
    const archiveWorkspace = useSelector(
        (store:any) => store.workspacelist.archivelist
    );
    const companyId = getCompanyId(user);
    const selectedWorkSpace = decryptedPersist(WORKSPACE);
    const [loading, setLoading] = useState(false);
    const { createBrain } = useBrains({isShare: true});
    if (!addMember && !addTeam) {
        Object.assign(defaultValue, { title: '' });
    }

    const {
        register,
        handleSubmit,
        formState: { errors },
        control,
        setValue: setFormValue,
        clearErrors,
        reset,
    } = useForm({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        defaultValues: defaultValue,
        resolver: addMember
            ? yupResolver(addMemberWorkSpaceKeys)
            : addTeam
            ? yupResolver(workspaceTeamSchema)
            : yupResolver(addWorkSpaceKeys),
    });

    const getWorkSpaceUsers = async (search) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.USER,
                common: true,
                data: {
                    options: {
                        sort: {
                            createdAt: DEFAULT_SORT,
                        },
                        pagination: false,
                    },
                    query: {
                        searchColumns: [SEARCH_AND_FILTER_OPTIONS.EMAIL],
                        search,
                        // invitedBy: companyId,
                        'company.id': companyId,
                        // $or: [
                        //     { 'company.id': companyId }, // 'company.id' must be a complete key-value pair
                        //     { invitedBy: companyId }
                        // ],
                        email: { $ne: user?.email },
                        inviteSts: USER_STATUS.ACCEPT
                    },
                },
            });
            setUsers(response.data);
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    const createWorkSpace = async (
        data,
        workspacename,
        roleCode,
        close,
        teamsInput
    ) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.WORKSPACE,
                data: {
                    title: workspacename,
                    users: data.map((u) => {
                        const obj = {
                            fname: u.fname,
                            lname: u.lname,
                            email: u.email,
                            id: u.id,
                            roleCode: u.roleCode,
                        }
                        return obj;
                    }),
                    teams: teamsInput.map((currTeam) => ({
                        id: currTeam.id,
                        teamName: currTeam.teamName,
                        teamUsers: currTeam.teamUsers,
                    })),
                },
                common: true,
            });
            Toast(response.message);
            dispatch(addWorkspaceListAction(response.data));

            // Warning: Don't add await here, it will block the main thread
                createBrain({ 
                    isShare: true, 
                    title: GENERAL_BRAIN_TITLE, 
                    workspaceId: response.data._id, 
                    members: data, 
                    teamsInput: teamsInput 
                }, close).catch(error => {
                    console.error('Error creating brain in background:', error);
                });

            close();
            return true;
        } catch (error) {
            console.log('error: ', error);
        } finally {
            close()
        }
    };

    const editWorkSpace = async (slug, data, close) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.UPDATE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.WORKSPACE,
                data: data,
                common: true,
                parameters: [slug],
            });
            Toast(response.message);
            dispatch(editWorkspaceListAction(response.data));

            if (selectedWorkSpace._id == data.id && response?.code!='ERROR') {
                let updatedTitleWorkspace = {
                    ...selectedWorkSpace,
                    title: data.title,
                };
                encryptedPersist(updatedTitleWorkspace, WORKSPACE);
            }
            setIsEdit(false);

            return response
        } catch (error) {
            console.log('error: ', error);
        }finally{
            close()
        }
    };

    const deleteWorkSpace = async (slug, id) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.WORKSPACE,
                common: true,
                parameters: [slug],
            });
            Toast(response.message);
            const updatedObj = removeObjectFromArray(workspacelist, id);
            dispatch(setWorkSpaceListAction(updatedObj));
        } catch (error) {
            console.log('error: ', error);
        }
    };

    const hardDeleteWorkSpace = async (data, slug, id, closeModal) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.WORKSPACE,
                common: true,
                parameters: [slug],
                data: {
                    isHardDelete: true,
                },
            });
            Toast(response.message);
            const updatedObj = removeObjectFromArray(archiveWorkspace, id);
            dispatch(setArchiveWorkSpace(updatedObj));
            closeModal();
        } catch (error) {
            console.log('error: ', error);
        } finally {
            close();
        }
    };

    const hardDeleteAllWorkSpace = async (closeModal, companyId) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.DELETEALL,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.WORKSPACE,
                common: true,
                data: {
                    companyId: companyId,
                },
            });
            Toast(response.message);
            dispatch(setArchiveWorkSpace([]));
            closeModal();
        } catch (error) {
            console.log('error: ', error);
        } finally {
            close();
        }
    };

    return { 
        users, 
        getWorkSpaceUsers, 
        register, 
        handleSubmit, 
        errors, hardDeleteWorkSpace, hardDeleteAllWorkSpace,
        createWorkSpace, editWorkSpace, deleteWorkSpace,
        control, setFormValue, reset, 
        isEdit, setIsEdit, loading, clearErrors
    };
};

export default useWorkspace;
