import { LINK } from '@/config/config';
import React from 'react';
import { MarkOutPut } from './MartOutput';
import ThreeDotLoader from '../Loader/ThreeDotLoader';
import { API_TYPE_OPTIONS, WEB_RESOURCES_DATA } from '@/utils/constant';
import DocumentProcessing from '../Loader/DocumentProcess';
import PreviewImage from '../ui/PreviewImage';
import CanvasInput from './CanvasInput';
import useCanvasInput from '@/hooks/chat/useCanvasInput';
import AgentAnalyze from '../Loader/AgentAnalyze';
import PageSpeedResponse from './PageSpeedResponse';
import { PAGE_SPEED_RECORD_KEY } from '@/hooks/conversation/useConversation';
import { ProAgentCode } from '@/types/common';
import WebAgentLoader from '../Loader/WebAgentLoader';
import VideoCallAgentLoader from '../Loader/VideoCallAgentLoader';
import SalesCallLoader from '../Loader/SalesCallLoader';
import ShowResources from './ShowResources';
type ResponseLoaderProps = {
    code: string;
    loading: boolean;
    proAgentCode: string;
}

export const GeneratedImagePreview = ({ src }) => {
    return (
        <PreviewImage
            src={src}
            actualWidth={300}
            actualHeight={300}
            previewWidth={500}
            previewHeight={500}
            className='max-w-[300px]'
        />
    );
};

const DallEImagePreview = ({
    conversations,
    i,
    loading,
    answerMessage,
    response,
}) => {
    return (
        <div className=" flex flex-col items-start gap-4 break-words min-h-5">
            <div className="chat-content max-w-none w-full break-words text-font-16 leading-7 tracking-[0.16px]">
                {conversations.length - 1 == i ? (
                    <>
                        {loading ? (
                            <ThreeDotLoader />
                        ) : answerMessage != '' ? (
                            <GeneratedImagePreview
                                src={`${LINK.AWS_S3_URL}/${answerMessage}`}
                            />
                        ) : (
                            <GeneratedImagePreview
                                src={`${LINK.AWS_S3_URL}/${response}`}
                            />
                        )}
                    </>
                ) : (
                    <GeneratedImagePreview
                        src={`${LINK.AWS_S3_URL}/${response}`}
                    />
                )}
            </div>
        </div>
    );
};

const StreamingChatLoaderOption = ({ code, loading, proAgentCode }: ResponseLoaderProps) => {
    const loadingComponents = {
        [API_TYPE_OPTIONS.OPEN_AI_WITH_DOC]: <DocumentProcessing />,
        [ProAgentCode.QA_SPECIALISTS]: <AgentAnalyze loading={loading} />,
        [ProAgentCode.WEB_PROJECT_PROPOSAL]: <WebAgentLoader loading={loading} />,
        [ProAgentCode.VIDEO_CALL_ANALYZER]: <VideoCallAgentLoader loading={loading} />,
        [ProAgentCode.SALES_CALL_ANALYZER]: <SalesCallLoader loading={loading} />,
    };
    return loadingComponents[code] || loadingComponents[proAgentCode] || <ThreeDotLoader />;
};

const ChatResponse = ({ conversations, i, loading, answerMessage, m, handleSubmitPrompt, privateChat = true, isStreamingLoading, proAgentCode }) => {
    const { 
        showCanvasBox, 
        handleSelectionChanges, 
        handleDeSelectionChanges, 
        selectedId, 
        showCanvasButton,
        handleAskWeam,
        buttonPosition,
        inputPosition,
        containerRef,
    } = useCanvasInput();

    const selectedMessage = selectedId === m?.id;
    const openCanvasButton = showCanvasButton && privateChat && !loading;
    const notProAgent = m?.responseAPI !== API_TYPE_OPTIONS.PRO_AGENT;
    const showRefineButton = selectedMessage && openCanvasButton && notProAgent;
   
    return m?.response?.startsWith('images') ? (
        <DallEImagePreview
            conversations={conversations}
            i={i}
            loading={loading}
            answerMessage={answerMessage}
            response={m.response}
        />
    ) : (
        <div className="flex flex-col items-start gap-4 break-words min-h-5">
            <div 
                className={`chat-content relative ${
                    m?.responseAPI !== API_TYPE_OPTIONS.PRO_AGENT ? 'max-w-[calc(100vw-95px)] lg:max-w-none' : ''
                } w-full break-words text-font-14 md:text-font-16 leading-7 tracking-[0.16px]`}
                onMouseUp={() => {
                    handleSelectionChanges(m?.id, m?.response)
                }}
                ref={containerRef}
            >
            {conversations.length - 1 === i ? (
                <>
                    {loading ? (
                        <StreamingChatLoaderOption code={m.responseAPI} loading={loading} proAgentCode={proAgentCode} />
                    ) : answerMessage !== '' ? (
                        MarkOutPut(answerMessage) //running stream response
                    ) :
                    //when stream response give done we empty answerMessage and show m.response (so in DB )
                    (
                        <>
                            {MarkOutPut(m.response)}
                            {
                                m?.responseAddKeywords?.hasOwnProperty(PAGE_SPEED_RECORD_KEY) 
                                ? <PageSpeedResponse response={m?.responseAddKeywords} /> : m?.responseAddKeywords?.hasOwnProperty('file_url') 
                                ? <div className="mt-4">{MarkOutPut(m.responseAddKeywords.file_url)}</div> : ''
                            }
                            {
                                m?.responseAddKeywords?.hasOwnProperty(WEB_RESOURCES_DATA) && <ShowResources response={m?.responseAddKeywords} />
                            }
                        </>
                    )}
                    {
                        (m?.responseAPI === API_TYPE_OPTIONS.PRO_AGENT && isStreamingLoading && answerMessage.length > 0) && (
                            <div className="my-2 animate-pulse text-font-14 font-bold inline-block">
                                <p>Checking next step...</p>
                            </div>   
                        )
                    }
                </>
            ) : (
                <>
                    {MarkOutPut(m.response)}
                    {
                        m?.responseAddKeywords?.hasOwnProperty(PAGE_SPEED_RECORD_KEY) && <PageSpeedResponse response={m?.responseAddKeywords} />
                    }
                    {
                        m?.responseAddKeywords?.hasOwnProperty(WEB_RESOURCES_DATA) && <ShowResources response={m?.responseAddKeywords} />
                    }
                </>
            )}
            {showRefineButton && (
                <button 
                className='btn btn-black min-w-[100px] px-3 py-[5px]'
                    style={{ ...buttonPosition }} 
                    onMouseDown={(e) => e.preventDefault()} 
                    onClick={handleAskWeam}
                >
                    Edit selected text
                </button>
            )}
    
            {/* Show the textbox if the button was clicked */}
            { privateChat && showCanvasBox && selectedId === m?.id && (
                <CanvasInput inputPosition={inputPosition} handleDeSelectionChanges={handleDeSelectionChanges} handleSubmitPrompt={handleSubmitPrompt}/>
            )}
        </div>
    </div>
    );
};

export default React.memo(ChatResponse);
