'use server';

import { MODULE_ACTIONS, MODULES, RESPONSE_STATUS, REVALIDATE_TAG_NAME } from '@/utils/constant';
import { serverApi, revalidateTagging } from './serverApi';
import { revalidateTag } from 'next/cache';
import { getSessionUser } from '@/utils/handleAuth';

export const addTeamAction = async (workspaceId, companyId, brainId, teams, title) => {
    const response = await serverApi({
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
    if (response.status === RESPONSE_STATUS.SUCCESS) {
        revalidateTag(`${REVALIDATE_TAG_NAME.TEAM}-${brainId}`);
    }
    return response;
}

export const getAllTeamAction = async () => {
    const response = await serverApi({
        action: MODULE_ACTIONS.LIST,
        prefix: MODULE_ACTIONS.WEB_PREFIX,
        module: MODULES.TEAM,
        common: true,
    });
    return response;
}

export const updateTeamAction = async (data) => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
            action: MODULE_ACTIONS.UPDATE,
            prefix: MODULE_ACTIONS.ADMIN_PREFIX,
            module: MODULES.TEAM,
            parameters: [data.teamId],
            data,
            common: true,
        });
    await revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`);
    await revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`);
    return response;
};

export const deleteTeamAction = async (teamId,allWorkspaceList) => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
        action: MODULE_ACTIONS.DELETE,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        module: MODULES.TEAM,
        parameters: [teamId],
        data:{
            allWorkspaceList
        },
        common: true,
    });

    await revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`);
    await revalidateTagging(response, `${REVALIDATE_TAG_NAME.WORKSPACE}-${sessionUser.companyId}`);
    return response;
}