'use server';

import { MODULE_ACTIONS } from '@/utils/constant';
import { serverApi } from './serverApi';
import { LoginPayload } from '@/types/user';
import { CompanyDetailSchemaType } from '@/schema/company';

export async function loginAction(payload: LoginPayload) {
    const response = await serverApi({
        action: MODULE_ACTIONS.LOGIN,
        module: MODULE_ACTIONS.AUTH,
        prefix: MODULE_ACTIONS.ADMIN_PREFIX,
        data: { email: payload.email.toLowerCase(), password: payload.password },
        common: true,
    });
    return response;
}

export const registerAction = async (details: CompanyDetailSchemaType & { country: { nm: string, shortCode: string } }) => {
    const registerdata = {
        fname: details.firstName,
        lname: details.lastName,
        email: details.email.toLowerCase(),
        password: details.password,
        confirmPassword: details.confirmPassword,
        companyNm: details.companyNm,
        countryName: details?.country?.nm,
        countryCode: details?.country?.shortCode,
    }
    const response = await serverApi({
        action: MODULE_ACTIONS.REGISTER_COMPANY,
        data: registerdata
    })
    return response;
}
