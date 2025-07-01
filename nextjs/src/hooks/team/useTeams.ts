import commonApi from '@/api';
import { teamSchema } from '@/schema/team';
import { removeObjectFromArray } from '@/utils/common';
import { DEFAULT_SORT, MODULE_ACTIONS, MODULES } from '@/utils/constant';
import { getCompanyId, getCurrentUser } from '@/utils/handleAuth';
import Toast from '@/utils/toast';
import { yupResolver } from '@hookform/resolvers/yup';
import {  useState } from 'react';
import { useForm } from 'react-hook-form';
export const useTeams = () => {
    const [loading, setLoading] = useState(false);
    const [teams, setTeams] = useState([]);

    const [brainAddedTeam, setBrainAddedTeam] = useState([]);
    const [totalRecords, setTotalRecords] = useState(0);

    const [tableLoader, setTableLoader] = useState(true);

    const {
        register,
        handleSubmit,
        formState: { errors, isDirty, dirtyFields },
        setValue: setFormValue,
        clearErrors,
        control,
        watch,
        reset,
    } = useForm({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        defaultValues: { teamName: '', members: [] },
        resolver: yupResolver(teamSchema),
    });


    const getTeams = async ({
        search,
        pagination = true,
        limit = 10,
        offset = 0,
        sort = '-1',
        sortby = 'id',
        workspaceUsers = false,
        brainUsers = false,
    }) => {
        try {
            setLoading(true);

            const currentUser = getCurrentUser();
            const companyId = getCompanyId(currentUser);

            const query = {
                companyId,
                search: search, 
                searchColumns: ["teamName"]
            };

            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.TEAM,
                common: true,
                data: {
                    options: {
                        ...(pagination
                            ? { offset, limit }
                            : { pagination: false }),
                        sort: {
                            createdAt: DEFAULT_SORT,
                        },
                        ...(workspaceUsers && { workspaceUsers }),
                        ...(brainUsers && { brainUsers }),
                    },
                    query,
                },
            });

            setTeams(response.data.data || []);
            setTotalRecords(response?.data.paginator?.itemCount);
            setTableLoader(false);
        } catch (error) {
            console.error(`Error in the get Team ::: ${error}`);
        } finally {
            setLoading(false);
        }
    };

    const createTeam = async (data, close) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.TEAM,
                common: true,
                data,
            });

            if(response?.code != "ERROR")
            setTeams((prev) => [response.data,...prev ]);
            setTotalRecords((prev)=>prev+1)
            Toast(response.message);
            return true;
        } catch (error) {
            console.error(`Error in create Team ::: ${error}`);
        }finally{
            setLoading(false);
        }
    };

    const updateTeam = async (data) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.UPDATE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.TEAM,
                parameters: [data.teamId],
                data,
                common: true,
            });

            Toast(response.message);

            setTeams((prevTeams) => {
                return prevTeams.map((team) =>
                    team._id === data.teamId
                        ? {
                              ...team,
                              teamName: data.teamName,
                              teamUsers: data.members,
                          }
                        : team
                );
            });

            return true;
        } catch (error) {
            console.error('Error in update team ::: ', error);
        }finally{
            setLoading(false);
        }
    };

    const deleteTeam = async (teamId,allWorkspaceList) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.ADMIN_PREFIX,
                module: MODULES.TEAM,
                parameters: [teamId],
                data:{
                    allWorkspaceList
                },
                common: true,
            });

            const updatedObj = removeObjectFromArray(teams, teamId);
            setTeams(updatedObj || []);
            setTotalRecords((prev)=>prev-1)
            Toast(response.message);
        } catch (error) {
            setTeams(teams);
            console.error('Error in delete team ::: ', error);
        }finally{
            setLoading(false);
        }
    };

    //  team list in workspace,brain and chat
    const sharedTeamBrainList = async ({ brainId, workspaceId,chatId }:any) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.TEAM_BRAIN,
                common: true,
                data: {
                    options: {
                        sort: {
                            createdAt: DEFAULT_SORT,
                        },
                        pagination: false,
                    },
                    query: {
                        ...(brainId && {
                            'brain.id': brainId,
                            brain: { $exists: true },
                        }),
                        ...(workspaceId && {
                            workspaceId: workspaceId,
                            brain: { $exists: false },
                        }),
                        ...(chatId && {
                            chatId: chatId,
                            
                        }),

                    },
                },
            });

            setBrainAddedTeam(response.data.teams || []);
        } catch (error) {
            console.error('Error in sharedTeamBrainList ::: ', error);
        }finally{
            setLoading(false);
        }
    };

    //update the team list in workspace (add in update workspace modal)
    const shareTeamWorkspace = async (workspaceId, companyId, teams, title) => {
        try {
            setLoading(true);

            const response = await commonApi({
                action: MODULE_ACTIONS.UPDATE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.TEAM_WORKSPACE,
                parameters: [workspaceId],
                data: {
                    companyId,
                    teams,
                    title,
                    workspaceId,
                },
                common: true,
            });

            Toast(response.message);
            setLoading(false);

            return true;
        } catch (error) {
            console.error(`Error in shareTeamWorkspace ::: `, error);
        } finally {
            close();
        }
    };

    //update the team list in brain (add brain modal)
    const shareTeamToBrain = async (
        workspaceId,
        companyId,
        brainId,
        teams,
        title
    ) => {
        try {
            setLoading(true);

            const response = await commonApi({
                action: MODULE_ACTIONS.UPDATE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.TEAM_BRAIN,
                parameters: [brainId],
                data: {
                    workspaceId,
                    companyId,
                    teams,
                    title,
                },
                common: true,
            });

            Toast(response.message);
            setLoading(false);

            return true;
        } catch (error) {
            console.error(`Error in shareTeamToBrain ::: `, error);
        } finally {
            close();
        }
    };

    //remove team from brain/workspace list
    const deleteShareTeamToBrain = async (
        workspaceId,
        companyId,
        brainId,
        teamId
    ) => {
        try {
            setLoading(true);

            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.TEAM_BRAIN,
                parameters: [teamId],
                data: {
                    workspaceId,
                    companyId,
                    ...(brainId && { brainId }),
                },
                common: true,
            });

            Toast(response.message);
            setLoading(false);
        } catch (error) {
            console.error(`Error in deleteShareTeamToBrain ::: `, error);
        } finally {
            close();
        }
    };

    //remove team from /workspace list
    const deleteShareTeamToWorkspace = async (
        workspaceId,
        companyId,
        teamId,
        sharedBrains
    ) => {
        try {
            setLoading(true);

            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.TEAM_WORKSPACE,
                parameters: [teamId],
                data: {
                    workspaceId,
                    companyId,
                    sharedBrains
                },
                common: true,
            });

            Toast(response.message);
            setLoading(false);
        } catch (error) {
            console.error(`Error in deleteShareTeamToBrain ::: `, error);
        } finally {
            close();
        }
    };

     //remove team from /workspace list
     const deleteShareTeamToChat = async (
         companyId,
         workspaceId,
         brainId,
         chatId,
         teamId,
    ) => {
      
        try {
            setLoading(true);

            const response = await commonApi({
                action: MODULE_ACTIONS.CHAT_TEAM_DELETE,
                data: {
                    companyId,
                    workspaceId,
                    brainId,
                    chatId,
                    
                },
                parameters: [teamId],
                
            });

            Toast(response.message);
          
        } catch (error) {
            console.error(`Error in deleteShareTeamToChat ::: `, error);
        }finally{
            setLoading(false);
        }
    };

    return {
        createTeam,
        getTeams,
        updateTeam,
        deleteTeam,
        sharedTeamBrainList,
        shareTeamWorkspace,
        shareTeamToBrain,
        deleteShareTeamToWorkspace,
        deleteShareTeamToBrain,
        deleteShareTeamToChat,
        teams,
        brainAddedTeam,
        setTeams,
        loading,
        register,
        clearErrors,
        errors,
        handleSubmit,
        control,
        setFormValue,
        watch,
        isDirty,
        reset,
        totalRecords,
        setTotalRecords
    };
};
