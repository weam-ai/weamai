import { serverApi } from './serverApi';
import { DEFAULT_SORT, MODULES, MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';

export default async function CustomPromptAction(searchValue:any, selectedTag:any) {
    const response = await serverApi({
        action: MODULE_ACTIONS.LIST,
        prefix: MODULE_ACTIONS.WEB_PREFIX,
        module: MODULES.PROMPT,
        common: true,
        data: {
            options: {
                sort: {
                    createdAt: DEFAULT_SORT
                },
                pagination: false
            },
            query: {
                searchColumns: [SEARCH_AND_FILTER_OPTIONS.NORMAL_TITLE],
                search: searchValue,
                defaultprompt: true,
                ...(selectedTag && { tags: { $in: [selectedTag] } }) 
            },
        },
    })

    return response.data;
}