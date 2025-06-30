'use server';

import { MODULE_ACTIONS } from '@/utils/constant';
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
