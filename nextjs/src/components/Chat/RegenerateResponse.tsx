import React, { useCallback, useMemo, useState } from 'react';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import Link from 'next/link';
import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/lib/store';
import RegenerateIcon from '@/icons/RegenerateIcon';
import LineArrowIcon from '@/icons/LineArrowIcon';
import { AiModalType } from '@/types/aimodels';
import { AgentChatPayloadType, ConversationType, DocumentChatPayloadType, NormalChatPayloadType, UploadedFileType } from '@/types/chat';
import { AI_MODAL_NAME, API_TYPE_OPTIONS, SUBSCRIPTION_STATUS } from '@/utils/constant';
import { Socket } from 'socket.io-client';
import { allowImageConversation, allowImageGeneration, getModelCredit } from '@/utils/helper';
import { setCreditInfoAction } from '@/lib/slices/chat/chatSlice';
import { modelNameConvert } from '@/utils/common';
import { getResponseModel, DEEPSEEK_WORD } from './UploadFileInput';

type RegenerateResponseProps = {
    conversation: ConversationType[],
    socket: Socket,
    chatId: string,
    getAINormatChatResponse: (payload: NormalChatPayloadType, socket: Socket) => void,
    getAICustomGPTResponse: (payload: AgentChatPayloadType, socket: Socket) => void,
    getPerplexityResponse: (socket: Socket, payload: unknown) => void,
    getAIDocResponse: (payload: DocumentChatPayloadType, socket: Socket) => void,
    setConversations: (payload: unknown) => ConversationType[],
    custom_gpt_id: string
}


const RegenerateResponse = React.memo(({ conversation, chatId, socket, getAINormatChatResponse, getAICustomGPTResponse, getPerplexityResponse, getAIDocResponse, setConversations, custom_gpt_id }: RegenerateResponseProps) => {
    const [isPopoverOpen, setIsPopoverOpen] = useState(false);
    const modals = useSelector((store: RootState) => store.assignmodel.list);
    const lastMessage = useMemo(() => conversation[conversation.length - 1], []);
    const dispatch = useDispatch();
    const creditInfo = useSelector((store: RootState) => store.chat.creditInfo);
    
    const hasImage = lastMessage.response.startsWith('images');
    const hasUploadedImage = Array.isArray(lastMessage.cloneMedia) && lastMessage.cloneMedia.some((file: UploadedFileType) => file.mime_type?.startsWith('image/'));
    const webSearch = [AI_MODAL_NAME.SONAR, AI_MODAL_NAME.SONAR_REASONING_PRO].includes(lastMessage.responseModel);

    const modalList = [];

    modals.forEach((modal: AiModalType) => {
        if (modal.isDisable) return;
        const modelName = modelNameConvert(modal.bot.code, modal.name);
        if (hasImage) {
            const allowImage = allowImageGeneration(modal.name);
            if (!allowImage) modalList.push({ ...modal, name: modelName, isDisable: true });
            else modalList.push({ ...modal, name: modelName });
            return;
        }
        if ([API_TYPE_OPTIONS.OPEN_AI_WITH_DOC, API_TYPE_OPTIONS.OPEN_AI_CUSTOM_GPT_WITH_DOC].includes(lastMessage.responseAPI)) {
            const hasWebSearch = [AI_MODAL_NAME.SONAR, AI_MODAL_NAME.SONAR_REASONING_PRO].includes(modal.name);
            if (hasWebSearch) modalList.push({ ...modal, name: modelName, isDisable: true });
            else modalList.push({ ...modal, name: modelName });
            return;
        }
        if (hasUploadedImage) {
            const imageConversation = allowImageConversation(modal);
            if (!imageConversation) modalList.push({ ...modal, name: modelName, isDisable: true });
            else modalList.push({ ...modal, name: modelName });
            return;
        }
        if (webSearch) {
            if ([AI_MODAL_NAME.SONAR, AI_MODAL_NAME.SONAR_REASONING_PRO].includes(modal.name)) modalList.push({ ...modal, name: modelName });
            else modalList.push({ ...modal, name: modelName, isDisable: true });
            return;
        }
        modalList.push({ ...modal, name: modelName });
    });

    const handleModelChange = useCallback((model: AiModalType) => {
        if (model.isDisable) return;
        setIsPopoverOpen(false);
        const isWebSearch = [AI_MODAL_NAME.SONAR, AI_MODAL_NAME.SONAR_REASONING_PRO].includes(model.name);
        const matchedModel = model.name.startsWith(DEEPSEEK_WORD) 
                        ? modals.find((modal) => modal._id === model._id).name 
                        : model.name;
        setConversations((prevConversations: ConversationType[]) => {
            const updatedConversations = [...prevConversations];
            const lastConversation = { ...updatedConversations[updatedConversations.length - 1] };
            lastConversation.responseModel = matchedModel;
            const lastConversationModel = { ...lastConversation.model };
            lastConversationModel.id = model._id;
            lastConversationModel.code = model.bot.code;
            lastConversation.model = lastConversationModel;
            updatedConversations[updatedConversations.length - 1] = lastConversation;
            return updatedConversations;
        });
        const payload = {
            messageId: lastMessage.id,
            text: lastMessage.message,
            prompt_id: lastMessage.promptId,
            modelId: model._id,
            chatId: chatId,
            code: model.bot.code,
            model_name: matchedModel,
            provider: model.provider,
            isregenerated: true,
            media: lastMessage.cloneMedia,
            msgCredit: getModelCredit(matchedModel)
        }
        if (lastMessage.responseAPI === API_TYPE_OPTIONS.OPEN_AI && !isWebSearch) {
            getAINormatChatResponse({ ...payload, img_url: lastMessage?.img_url }, socket);
        } else if (lastMessage.responseAPI === API_TYPE_OPTIONS.OPEN_AI_WITH_DOC) {
            getAIDocResponse(payload, socket);
        } else if (lastMessage.responseAPI === API_TYPE_OPTIONS.OPEN_AI_CUSTOM_GPT_WITH_DOC) {
            const customGptId = typeof lastMessage.customGptId === 'string' ? lastMessage.customGptId : lastMessage?.customGptId?._id;
            getAICustomGPTResponse({ ...payload, custom_gpt_id: customGptId || custom_gpt_id }, socket);
        } else if (lastMessage.responseAPI === API_TYPE_OPTIONS.PERPLEXITY || lastMessage.responseAPI === API_TYPE_OPTIONS.OPEN_AI) {
            getPerplexityResponse(socket, payload);
        }
        const updatedCreditInfo = {
            ...creditInfo,
            msgCreditUsed: creditInfo.msgCreditUsed + payload.msgCredit
        };
        dispatch(setCreditInfoAction(updatedCreditInfo));
    }, [creditInfo]);
    
    return (
        <span className="cursor-pointer flex items-center justify-center h-8 min-w-8 rounded-custom p-1 transition ease-in-out duration-150 hover:bg-b12 regenerate-response">
            <TooltipProvider>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <span>
                            <Popover open={isPopoverOpen} onOpenChange={setIsPopoverOpen}>
                                <PopoverTrigger asChild>
                                    <Link
                                        href="#"
                                        className="flex items-center"
                                    >
                                        <RegenerateIcon
                                            width={13}
                                            height={13}
                                            className="h-[13px] w-[13px] fill-b6 object-contain"
                                        />
                                        

                                        <span className={`text-font-12 ml-1 ${isPopoverOpen ? 'block' : 'hidden'}`}>
                                            {getResponseModel(lastMessage?.responseModel)}
                                        </span>
                                        <LineArrowIcon
                                            width={10}
                                            height={10}
                                            className="fill-b6 w-[10px] h-[10px] -rotate-90 ml-1"
                                        />
                                    </Link>
                                </PopoverTrigger>
                                <PopoverContent className="w-52 px-2 py-5 border-b11 rounded-10 overflow-y-auto max-h-[350px]">
                                    <h4 className="font-normal text-b7 text-font-14 pb-3 px-3">
                                        Switch Model
                                    </h4>
                                    <div className="flex flex-col text-font-14">
                                        {
                                            modalList.length > 0 && modalList.map((modal: AiModalType) => (
                                                <div key={modal._id} className={`items-center px-3 py-2 hover:bg-b12 rounded-md ${modal.isDisable ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}`} onClick={() => handleModelChange(modal)}>
                                                    {modal.name}
                                                </div>
                                            ))
                                        }
                                    </div>
                                </PopoverContent>
                            </Popover>
                        </span>
                    </TooltipTrigger>
                    <TooltipContent side="bottom">
                        <p className="text-font-14">Regenerate</p>
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        </span>
    );
});

export default RegenerateResponse;
