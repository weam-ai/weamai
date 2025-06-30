'use server';

import { serverApi } from '@/actions/serverApi';
import { getSession } from '@/config/withSession';
import { AiModalType } from '@/types/aimodels';
import { APIResponseType } from '@/types/common';
import { AI_MODAL_NAME, DEFAULT_SORT, MODULE_ACTIONS, MODULES, SEQUENCE_MODEL_LIST } from '@/utils/constant';

export async function fetchAiModal(): Promise<APIResponseType<AiModalType[]>> {
    const session = await getSession();
    const companyId = session?.user?.companyId;
    const response = await serverApi({
        action: MODULE_ACTIONS.LIST,
        module: MODULES.USER_MODEL,
        prefix: MODULE_ACTIONS.WEB_PREFIX,
        data: {
            options: {
                // sort: { createdAt: DEFAULT_SORT },
                pagination: false,
            },
            query: {
                $and: [
                    {
                        modelType: { $exists: true },
                    },
                    {
                        modelType: { $ne: 1 },
                    },
                    {
                        'company.id': companyId,
                    }
                ]
            },   
        },
        config: { next: { revalidate: 86400 } },
        common: true,
    });
    if (response.data?.length > 0) {
        const orderedList = response.data?.reduce((acc: any, item: any) => {
            const index = SEQUENCE_MODEL_LIST.indexOf(item?.bot?.code);
            if (index !== -1) {
                acc[index] = acc[index] || [];
                acc[index].push(item);
            }
            return acc;
        }, []).flat();


        const modelNameMap = new Map<string, AiModalType>();
        orderedList.forEach((item: AiModalType) => {
            modelNameMap.set(item.name, item);
        });

        // internal sequence
        const modelNames = Object.values(AI_MODAL_NAME)

        const filteredModelList = modelNames.reduce((acc: AiModalType[], current:string) => {
            const findPushModel = modelNameMap.get(current)
            if (findPushModel) {
                acc.push(findPushModel)
            }
            return acc
        }, [])
        return { ...response, data: filteredModelList };
    }
    return { ...response };
}
