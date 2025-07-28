'use server';
import { RESPONSE_STATUS, RESPONSE_STATUS_CODE } from '@/utils/constant';
import { FETCH_ACTION_HANDLERS, getHeaders, setAPIConfig, ConfigOptions } from '../api';
import { revalidateTag } from 'next/cache';
import { getSession } from '@/config/withSession';
import { LINK, NODE_API_PREFIX } from '@/config/config';

export async function getAccessToken() {
    const session = await getSession();
    return session?.user?.access_token;
}

async function fetchUrl({ type = 'GET', url, data = {}, config = {} }:any) {
    const actionType = type.toUpperCase();
    const handler = FETCH_ACTION_HANDLERS[actionType];

    const token = await getAccessToken();
    
    config.headers = await getHeaders({
        baseUrl: `${LINK.SERVER_NODE_API_URL}`,
        tokenPrefix: 'jwt',
        getToken: token,
    }, config);
    
    try {
        const response = await handler(url, data, config);
        return response;
    } catch (error) {
        const { status } = (error.response || {});
        const data = (error.data || {});
        if (status === RESPONSE_STATUS.FORBIDDEN && data.code === RESPONSE_STATUS_CODE.CSRF_TOKEN_MISSING) {
            return { status: RESPONSE_STATUS.FORBIDDEN, code: RESPONSE_STATUS_CODE.CSRF_TOKEN_MISSING }
        }
        if (status === RESPONSE_STATUS.FORBIDDEN || data.code === RESPONSE_STATUS_CODE.TOKEN_NOT_FOUND) {
            return { status: RESPONSE_STATUS.FORBIDDEN, code: RESPONSE_STATUS_CODE.TOKEN_NOT_FOUND }
        }
        // else if (status === RESPONSE_STATUS.UNAUTHENTICATED) {
        //     return { status: RESPONSE_STATUS.UNAUTHORIZED, code: RESPONSE_STATUS_CODE.REFRESH_TOKEN }
        // } 
        else if (status === RESPONSE_STATUS.UNPROCESSABLE_CONTENT) {
            return { status: RESPONSE_STATUS.UNPROCESSABLE_CONTENT, code: data.code, message: data.message }
        } else if (status === RESPONSE_STATUS.UNAUTHENTICATED) {
            return { status: RESPONSE_STATUS.FORBIDDEN, code: RESPONSE_STATUS_CODE.CSRF_TOKEN_NOT_FOUND }
        }
        return { status: RESPONSE_STATUS.ERROR, code: RESPONSE_STATUS_CODE.ERROR, message: data.message }
    }
}

export const setServerAPIConfig = (conf: ConfigOptions) => {
    setAPIConfig(conf);
    return conf
};


export async function serverApi({
    parameters = [],
    action,
    module = '',
    prefix = '',
    data,
    config = {},
    common = false,    
}:any) {
    const apiList = (await import('../api/list')).default;
    const api = common
        ? apiList.commonUrl(prefix, module)[action]
        : apiList[`${action}`];

    if (!api) {
        return { code: 'ERROR', message: 'Invalid API action or URL.' };
    }

    const token = await getAccessToken()
    // const tokenCookieValue = cookies().get('csrf_token')?.value;
    // const tokenCookieRawValue = cookies().get('weam_raw')?.value;
    // const csrfToken = tokenCookieValue ? decryptedData(tokenCookieValue) : '';
    // const csrfTokenRaw = tokenCookieRawValue ? decryptedData(tokenCookieRawValue) : '';
    setServerAPIConfig({
        getToken: token,
        baseUrl: `${LINK.SERVER_NODE_API_URL}${NODE_API_PREFIX}`,
        tokenPrefix: 'jwt',
    });

    const response = await fetchUrl({
        type: api.method,
        url: api.url(...parameters),
        data,
        config,
    });
    
    return response;
}

export async function revalidateTagging(response, tag: string) {
    if ([RESPONSE_STATUS.SUCCESS, RESPONSE_STATUS.CREATED].includes(response.status)) {
        revalidateTag(tag);
    }
}