'use server';

import { MODULE_ACTIONS, MODULES, RESPONSE_STATUS, REVALIDATE_TAG_NAME } from '@/utils/constant';
import { revalidateTagging, serverApi } from './serverApi';
import { getSessionUser } from '@/utils/handleAuth';

export const removeUserAction = async (userId: string) => {
    const sessionUser = await getSessionUser();
    const response = await serverApi({
        action: MODULE_ACTIONS.DELETE,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        module: MODULES.USER,
        parameters: [userId],
        common: true
    });
    
    await revalidateTagging(response, `${REVALIDATE_TAG_NAME.BRAIN}-${sessionUser.companyId}`);

    return response;
}