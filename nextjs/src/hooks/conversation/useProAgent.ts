import { useState } from 'react';
import useConversation from './useConversation';
import { API_PREFIX, LINK } from '@/config/config';
import { BusinessSummaryPayloadType, BusinessSummaryResponseType, SeoTopicGenerationPayloadType, SeoTopicGenerationResponseType } from '@/types/proAgents';
import { APIResponseType, ProAgentCode, ProAgentPythonCode } from '@/types/common';
import { TOKEN_PREFIX } from '@/utils/constant';

const useProAgent = () => {
    const [isLoading, setIsLoading] = useState(false);
    const { getCommonPythonPayload } = useConversation();
    const [leftList, setLeftList] = useState([]);
    const [rightList, setRightList] = useState([]);
    
    const generateAudienceAndSummary = async (payload: BusinessSummaryPayloadType)
        : Promise<APIResponseType<BusinessSummaryResponseType> | null> => {
        try {
            setIsLoading(true);
            const { companyId, token } = await getCommonPythonPayload();
            const response = await fetch(
                `${LINK.PYTHON_API_URL}${API_PREFIX}/agent/pro-agent/business-summary`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `${TOKEN_PREFIX}${token}`,
                    },
                    body: JSON.stringify({
                        company_id: companyId,
                        delay_chunk: 0.02,
                        pro_agent_code: ProAgentCode.SEO_OPTIMIZER,
                        agent_extra_info: {
                            project_name: payload.projectName,
                            location: payload.location.map((location) => location.value),
                            target_keywords: payload.keywords,
                            website_url: payload.url,
                            language: 'English',
                        },
                    }),
                }
            );
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error generating audience and summary', error);
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    const getSeoKeyWords = async (payload) => {
        try {
            setIsLoading(true);
            const { token, companyId } = await getCommonPythonPayload();
            const response = await fetch(
                `${LINK.PYTHON_API_URL}${API_PREFIX}/agent/pro-agent/keyword-research`,
                {
                    method: 'POST',
                    body: JSON.stringify({
                        thread_id: payload.thread_id,
                        query: payload.query,
                        chat_session_id: payload.chatId,
                        company_id: companyId,
                        delay_chunk: 0.02,
                        pro_agent_code: ProAgentCode.SEO_OPTIMIZER,
                        brain_id: payload.brain_id,
                        msgCredit: payload.msgCredit,
                        agent_extra_info: {
                            project_name: payload.proAgentData.projectName,
                            location: payload.proAgentData.location.map((location) => location.value),
                            target_keywords: payload.proAgentData.keywords,
                            website_url: payload.proAgentData.url,
                            business_summary: payload.proAgentData.summary,
                            target_audience: payload.proAgentData.audience,
                            language: 'English',
                        },
                    }),
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `${TOKEN_PREFIX}${token}`,
                    },
                }
            );
            
            const jsonReponse = await response.json();
            setLeftList(jsonReponse?.data?.targeted_keywords);
            setRightList(jsonReponse?.data?.recommended_keywords);
        } catch (error) {
            console.error('Error generating audience and summary', error);
            return null;
        } finally {
            setIsLoading(false);
        }
    }

    const generateSeoTopicName = async (payload: SeoTopicGenerationPayloadType)
        : Promise<APIResponseType<SeoTopicGenerationResponseType> | null> => {
        try {
            setIsLoading(true);
            const { companyId, token } = await getCommonPythonPayload();
            const response = await fetch(
                `${LINK.PYTHON_API_URL}${API_PREFIX}/agent/pro-agent/topic-generation`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `${TOKEN_PREFIX}${token}`,
                    },
                    body: JSON.stringify({
                        thread_id: payload.messageId,
                        company_id: companyId,
                        delay_chunk: 0.02,
                        pro_agent_code: ProAgentCode.SEO_OPTIMIZER,
                        agent_extra_info: {
                            secondary_keywords: payload.secondaryKeywords,
                            primary_keywords: [payload.primaryKeyword],
                        },
                    }),
                }
            );
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error generating seo topic name', error);
            return null;
        } finally {
            setIsLoading(false);
        }
    }

    

    return {
        generateAudienceAndSummary,
        isLoading,
        getSeoKeyWords,
        generateSeoTopicName,
        leftList,
        rightList,
        setLeftList,
        setRightList        
    };
};

export default useProAgent;
