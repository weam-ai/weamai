import { getResponseModel } from '@/components/Chat/UploadFileInput';
import { ProAgentCode, ProAgentComponentLable } from '@/types/common';
import { isEmptyObject } from '@/utils/common';
import { decodedObjectId, formatAgentRequestCopyData } from '@/utils/helper';
import Toast from '@/utils/toast';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useCallback } from 'react';

const useConversationHelper = () => {
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();

    const copyToClipboard = useCallback(async (content: string) => {
        await navigator.clipboard.writeText(content);
        Toast('Chat text copied');
    }, []);

    const handleModelSelectionUrl = useCallback((model: string) => {
        history.pushState(null, '', `${pathname}?b=${searchParams.get('b')}&model=${getResponseModel(model)}`);
    }, [router, pathname, searchParams]);

    const getDecodedObjectId = useCallback(() => {
        const brainId = searchParams.get('b');
        return decodedObjectId(brainId);
    }, [searchParams]);

    const blockProAgentAction = (isQuery: boolean = false, code?: string) => {
        const blockedAgents = [ProAgentComponentLable.SEO, ProAgentCode.SEO_OPTIMISED_ARTICLES];
        if (isQuery) {
            if (blockedAgents.includes(code as ProAgentComponentLable)) {
                return true;
            }
        } else {
            const agent = searchParams.get('agent');
            if (blockedAgents.includes(agent as ProAgentComponentLable)) {
                return true;
            }
        }
        return false;
    }

    const handleProAgentUrlState = useCallback((model: string, code: string) => {
        const agentCode = {
            [ProAgentCode.SEO_OPTIMISED_ARTICLES]: ProAgentComponentLable.SEO,
            [ProAgentCode.QA_SPECIALISTS]: ProAgentComponentLable.QA,
            [ProAgentComponentLable.SEO]: ProAgentComponentLable.SEO,
        }
        const agentName = agentCode[code];
        history.pushState(null, '', `${pathname}?b=${searchParams.get('b')}&model=${getResponseModel(model)}&agent=${agentName}`);
    }, [router, pathname, searchParams]);

    const getAgentContent = (proAgentData) => {
        let agentContent;

        if(!isEmptyObject(proAgentData)){
            switch (proAgentData?.code) {
                case ProAgentCode.SEO_OPTIMISED_ARTICLES:
                    const keywords = proAgentData?.keywords?.join(", ");
                    const locationValues = proAgentData?.location.map(location => location.value).join(", ");
                    agentContent = `Agent: ${proAgentData?.code.replace(/_/g, ' ')}, URL: ${proAgentData?.url}, Project Name: ${proAgentData?.projectName}, Locations: ${locationValues}, Targeted Keyword: ${keywords}, Target Audience: ${proAgentData?.audience}, Business Summary: ${proAgentData?.summary}`;
                    break;
                // case ProAgentCode.QA_SPECIALISTS:
                //     agentContent = formatAgentRequestCopyData(proAgentData, ['']);
                //     break;
                // case ProAgentCode.WEB_PROJECT_PROPOSAL:
                //     agentContent = formatAgentRequestCopyData(proAgentData, ['']);
                //     break;
                case ProAgentCode.VIDEO_CALL_ANALYZER:
                    agentContent = formatAgentRequestCopyData(proAgentData, ['fileInfo']);
                    break;
                default:
                    agentContent = formatAgentRequestCopyData(proAgentData, ['']);
                    break;
            }
        }
        return agentContent;
    }

    return {
        copyToClipboard,
        handleModelSelectionUrl,
        getDecodedObjectId,
        blockProAgentAction,
        handleProAgentUrlState,
        getAgentContent
    }
}

export default useConversationHelper