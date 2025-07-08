'use server';

import { MODULE_ACTIONS, MODULES } from '@/utils/constant';
import { serverApi } from './serverApi';

export const getStorageAction = async () => {
    const response = await serverApi({
        action: MODULE_ACTIONS.GET_STORAGE,
        config: { next: { revalidate: 60 } }
    });
    return response;
};

export const updateStorageAction = async (payload) => {
    const response = await serverApi({
        action: MODULE_ACTIONS.INCREASE_STORAGE,
        data: payload                
    })
    return response;
};

export const addConfigEnvAction = async (payload) =>{
    // const sessionUser = await getSessionUser();
    const response = await serverApi({
        action: MODULE_ACTIONS.CREATE,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        module: MODULES.CONFIGURATION_ENV,
        data: payload,
        common: true,
    })
    // revalidateTag(`${REVALIDATE_TAG_NAME.CONFIGURATION_ENV}-${sessionUser._id}`);
    return response;
}
