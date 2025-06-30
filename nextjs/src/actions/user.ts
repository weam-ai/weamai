'use server';
import { MODULE_ACTIONS, MODULES, REVALIDATE_TAG_NAME } from '@/utils/constant';
import { revalidateTagging, serverApi } from './serverApi';

export const getUserByIdAction = async (userId: string) => {
    const response = await serverApi({
        action: MODULE_ACTIONS.GET,
        prefix: MODULE_ACTIONS.WEB_PREFIX,
        module: MODULES.USER,
        parameters: [userId],
        common: true,
        config: {
            next: {
                revalidate: 86400,
                tags: [`${REVALIDATE_TAG_NAME.USER}-${userId}`],
            },
        },
    });

   

    return response;
};

export const toggleBrainAction = async (
    userIds: string[],
    toggleStatus: boolean,
    isAll: boolean
) => {
    const response = await serverApi({
        action: MODULE_ACTIONS.TOGGLE,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        module: MODULES.USER,
        data: {
            ...(isAll ? {} : { userIds }),
            toggleStatus,
        },
        common: true,
    });

    for (const key of userIds) {
        await revalidateTagging(response, `${REVALIDATE_TAG_NAME.USER}-${key}`);
    }
    return response;
};
