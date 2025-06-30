import { useState, useMemo } from 'react';
import { ConversationType } from '@/types/chat';
import SeoTopicGeneration from '../ProAgentAnswer/SeoTopicGeneration';
import SeoProAgentKeyword from '../ProAgentAnswer/SeoProAgentKeyword';
import { Socket } from 'socket.io-client';
import { keywordCheckBoxType, ProAgentDataResponseType } from '@/types/proAgents';

type SeoProAgentResponseProps = {
    conversation: ConversationType[];
    proAgentData: ProAgentDataResponseType;
    leftList: keywordCheckBoxType[];
    rightList: keywordCheckBoxType[];
    setLeftList: (leftList: keywordCheckBoxType[]) => void;
    setRightList: (rightList: keywordCheckBoxType[]) => void;
    isLoading: boolean;
    socket: Socket;
    generateSeoArticle: any;
    loading: boolean;
}

const SeoProAgentResponse = ({ conversation, proAgentData, leftList, rightList, setLeftList, setRightList, isLoading, socket, generateSeoArticle, loading }: SeoProAgentResponseProps) => {
    const lastMessage = conversation[conversation.length - 1];
    const [selectedKeywords, setSelectedKeywords] = useState([]);
    const [topicName, setTopicName] = useState('');
    const [primaryKeyword, setPrimaryKeyword] = useState('');
    const isStep3 = proAgentData?.hasOwnProperty('step3');

    const leftAssignedKeywords = useMemo(() => leftList.length > 0 ? leftList : proAgentData?.step2?.targeted_volumes, [leftList, proAgentData]);
    const rightAssignedKeywords = useMemo(() => rightList.length > 0 ? rightList : proAgentData?.step2?.recommended_volumes, [rightList, proAgentData]);
    const assignTopicName = useMemo(() => proAgentData?.step3?.topics || topicName, [proAgentData, topicName]);
    const assignKeywords = useMemo(() => proAgentData?.step3?.selected_keywords || selectedKeywords, [proAgentData, selectedKeywords]);
    return (
        <div className="flex flex-col gap-2">
            {!selectedKeywords.length && !isStep3 ?
                    <SeoProAgentKeyword 
                        isLoading={isLoading} 
                        leftList={leftAssignedKeywords} 
                        rightList={rightAssignedKeywords} 
                        setLeftList={setLeftList} 
                        setRightList={setRightList} 
                        setSelectedKeywords={setSelectedKeywords}
                        setTopicName={setTopicName}
                        messageId={lastMessage.id}
                        proAgentData={proAgentData}
                        primaryKeyword={primaryKeyword}
                        setPrimaryKeyword={setPrimaryKeyword}
                    />
                :
                    <>
                        <SeoTopicGeneration messageId={lastMessage.id} keywords={assignKeywords} topicName={assignTopicName} socket={socket} generateSeoArticle={generateSeoArticle} loading={loading} primaryKeyword={primaryKeyword} />
                    </>
            } 
        </div>
    );
};

export default SeoProAgentResponse;
