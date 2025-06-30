'use server';

import { getSessionUser } from '@/utils/handleAuth';
import { revalidateTagging, serverApi } from './serverApi';
import { GENERAL_BRAIN_TITLE, MODULE_ACTIONS, MODULES, RESPONSE_STATUS, REVALIDATE_TAG_NAME } from '@/utils/constant';
import { ObjectType } from '@/types/common';
import { createBrainAction } from './brains';


export const fetchWorkspaceList = async () => {
    try {
        const sessionUser = await getSessionUser();
        const response = await serverApi({
                action: MODULE_ACTIONS.LIST,
                module: MODULES.WORKSPACE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                data: {
                    options: {
                        pagination: false,
                    },
                    query: {
                        deletedAt: {
                            $exists: false,
                        },
                    },
                },
                config: { next: { revalidate: 86400, tags: [`${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`] } },
                common: true,
        });
        return response;
    } catch (error) {
        
    }
};

export const createWorkspaceAction = async (data) => {
    try {
        const sessionUser = await getSessionUser();
        const response = await serverApi({
            action: MODULE_ACTIONS.CREATE,
            module: MODULES.WORKSPACE,
            prefix: MODULE_ACTIONS.ADMIN_PREFIX,
            data: {
                title: data.title,
                users: data.members.map((u) => {
                    const obj = {
                        fname: u.fname,
                        lname: u.lname,
                        email: u.email,
                        id: u.id,
                        roleCode: u.roleCode,
                    }
                    return obj;
                }),
                teams: data.teamsInput.map((currTeam) => ({
                    id: currTeam.id,
                    teamName: currTeam.teamName,
                    teamUsers: currTeam.teamUsers,
                })),
            },
            common: true,
            config: { next: { revalidate: false } }
        });
        await Promise.all([
            revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`),
            revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`),
        ]);
        if (response.status === RESPONSE_STATUS.CREATED)
            createBrainAction({ isShare: true, title: GENERAL_BRAIN_TITLE, workspaceId: response.data._id, members: data.members, teamsInput: data.teamsInput });
        return response;
    } catch (error) {
        
    }
};

export async function editWorkSpaceAction(slug, data) {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
        action: MODULE_ACTIONS.UPDATE,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        module: MODULES.WORKSPACE,
        data: data,
        common: true,
        parameters: [slug],
    });
    await Promise.all([
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`),
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`),
    ]);
    return response;
};

export const archiveWorkspaceListAction = async () => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
        action: MODULE_ACTIONS.LIST,
        prefix: MODULE_ACTIONS.WEB_PREFIX,
        module: MODULES.WORKSPACE,
        common: true,
        data: {
            options: {
                pagination: false
            },
            query: { 
                deletedAt: {
                    $exists : true
                }
            }
        },
        config: { next: { revalidate: 86400, tags: [`${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`] } },
    });
    return response;
};

export const restoreWorkspaceAction = async (payload) => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
        action: MODULE_ACTIONS.RESTORE,
        prefix: MODULE_ACTIONS.WEB_PREFIX,
        module: MODULES.WORKSPACE,
        common: true,
        parameters: [payload?.slug]
    })
    await Promise.all([
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`),
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`),
    ]);
    return response;
};

export const hardDeleteWorkspaceAction = async (slug: string) => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
        action: MODULE_ACTIONS.DELETE,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        module: MODULES.WORKSPACE,
        common: true,
        parameters: [slug],
        data: { isHardDelete: true }
    });
    await Promise.all([
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`),
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`),
    ]);
    return response;
};

export const addWorkspaceMemberAction = async (workspaceId, companyId, users) => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
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
    await Promise.all([
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`),
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`),
    ]);
    return response;
}

export const shareTeamWorkspaceAction = async (workspaceId, companyId, teams, title) => {
    const response = await serverApi({
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
    await Promise.all([
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${companyId}`),
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${companyId}`),
    ]);
    return response;
}

export const archiveWorkspaceAction = async (slug: string) => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
        action: MODULE_ACTIONS.DELETE,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        module: MODULES.WORKSPACE,
        common: true,
        parameters: [slug],
    });
    await Promise.all([
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`),
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`),
    ]);
    return response;
}

export const deleteShareTeamToWorkspaceAction = async (workspaceId: string, companyId: string, teamId: string, sharedBrains: ObjectType[]) => {
    const response = await serverApi({
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
    await Promise.all([
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${companyId}`),
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${companyId}`),
    ]);
    return response;
};

export const removeWorkspaceMemberAction = async (workspaceId: string, userId: string, sharedBrains: ObjectType[]) => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
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
    await Promise.all([
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`),
        revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`),
    ]);
    return response;
}