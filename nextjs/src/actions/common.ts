'use server';
import { MODULE_ACTIONS, MODULES } from '@/utils/constant';
import { serverApi } from './serverApi';
import { APIResponseType, CountriesType } from '@/types/common';

export const getCountryListAction = async (): Promise<APIResponseType<CountriesType[]>> => {
    try {
        const response = await serverApi({
            action: MODULE_ACTIONS.LIST,
            module: MODULES.COUNTRY,
            prefix: MODULE_ACTIONS.COMMON_PREFIX,
            data: {
                options: {
                    pagination: false,
                },
            },
            common: true,
        });
        return response;
    } catch (error) {
        console.error('error: getCountryListAction', error);
    }
};
