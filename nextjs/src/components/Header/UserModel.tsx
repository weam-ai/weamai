'use client';

import { useEffect, useState, memo } from 'react';
import useAssignModalList from '@/hooks/aiModal/useAssignModalList';
import { useDispatch, useSelector } from 'react-redux';
import { setSelectedAIModal } from '@/lib/slices/aimodel/assignmodelslice';
import { isEmptyObject, modelNameConvert } from '@/utils/common';
import { usePathname, useSearchParams } from 'next/navigation';
import { AiModalType } from '@/types/aimodels';
import { RootState } from '@/lib/store';
import ChatTitleBar from './ChatTitleBar';
import UserModalPopOver from './UserModalPopOver';
import { AI_MODEL_CODE } from '@/utils/constant';

const UserModel = () => {
    const [open, setOpen] = useState(false);
    const { userModals, fetchSocketModalList } = useAssignModalList();
    const dispatch = useDispatch();
    const chatTitle = useSelector((store: RootState) => store.conversation.chatTitle);
    const lastConversationModal = useSelector((store: RootState) => store.conversation.lastConversation);
    const selectedAIModal = useSelector((store: RootState) => store.assignmodel.selectedModal);
    const queryParams = useSearchParams();
    const model = queryParams.get('model');
    const b = queryParams.get('b');
    const agent = queryParams.get('agent');
    const pathname = usePathname();
    
    useEffect(() => {
        if (!userModals || !userModals.length) return;
        if (lastConversationModal?.responseModel) {
            const selectedModal = userModals.find(el => el.name === lastConversationModal.responseModel);
             if(isEmptyObject(selectedAIModal)){
                const defaultModel = userModals.find(el => el.name === AI_MODEL_CODE.DEFAULT_OPENAI_SELECTED);
                if (defaultModel) {
                    dispatch(setSelectedAIModal(defaultModel));
                }
            }else{
                dispatch(setSelectedAIModal(selectedModal));
            }
        }
    }, [lastConversationModal])

    useEffect(() => {
        fetchSocketModalList();
    }, [])

    const handleModelChange = (model: AiModalType) => {
        setOpen(false);
        if (agent) return;
        const modelName = modelNameConvert(model.bot.code, model.name);
        history.pushState(null, '', `${pathname}?b=${b}&model=${modelName}`);
        dispatch(setSelectedAIModal(model));
    };
    


    return (
        <>
            {userModals.length > 0 && model && (
                <div className="header-left flex ml-0 items-center space-x-3">
                    <div className="relative">
                        <UserModalPopOver open={open} setOpen={setOpen} selectedAIModal={selectedAIModal} handleModelChange={handleModelChange} userModals={userModals} />
                    </div>
                    <ChatTitleBar chatTitle={chatTitle} />
                </div>
            )}
        </>
    );
};

export default memo(UserModel);