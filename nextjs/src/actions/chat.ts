'use server';

import { DEFAULT_LIMIT, DEFAULT_SORT, MODULE_ACTIONS, MODULES, RESPONSE_STATUS, REVALIDATE_TAG_NAME, SEARCH_AND_FILTER_OPTIONS } from "@/utils/constant";
import { serverApi } from "./serverApi";
import { decodedObjectId } from "@/utils/helper";
import { revalidateTag } from "next/cache";
import { APIResponseType } from "@/types/common";
import { SubscriptionActionStatusType } from "@/types/subscription";

export const getChatListAction = async (filter) => {
    const { user, bid, search, page } = filter;
    const brainId = decodedObjectId(bid);
    const response = await serverApi({
        action: MODULE_ACTIONS.LIST,
        prefix: MODULE_ACTIONS.WEB_PREFIX,
        module: MODULES.CHAT_MEMBER,
        common: true,
        data: {
            options: {
                sort: { createdAt: DEFAULT_SORT },
                limit: DEFAULT_LIMIT,
                offset: (page - 1) * DEFAULT_LIMIT,
                populate: [
                    {
                        path: 'chatId',
                        select: 'title user'
                    }
                ]
            },
            query: {
                'user.id': user._id, isNewChat: false, 'brain.id': brainId,
                searchColumns: [SEARCH_AND_FILTER_OPTIONS.NORMAL_TITLE],
                search: search,
            }
        },
        config: { next: { tags: [`${REVALIDATE_TAG_NAME.CHAT}-${user._id}`], revalidate: 86400 } }
    })
    return response;
};

export const deleteChatAction = async (chatId, user) => {
    const response = await serverApi({
        action: MODULE_ACTIONS.DELETE,
        prefix: MODULE_ACTIONS.WEB_PREFIX,
        module: MODULES.CHAT,
        common: true,
        parameters: [chatId]
    })
    if (response.status == RESPONSE_STATUS.SUCCESS) revalidateTag(`${REVALIDATE_TAG_NAME.CHAT}-${user._id}`);
    return response;
};


export const getSubscriptionStatusAction = async (): Promise<APIResponseType<SubscriptionActionStatusType>> => {
    const response = await serverApi({
        action: MODULE_ACTIONS.GET_MESSAGE_CREDITS,
        config: { next: { revalidate: 30 } },
    })
    return response;
}