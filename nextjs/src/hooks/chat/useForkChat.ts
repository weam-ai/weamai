import commonApi from '@/api';
import { ForkChatType } from '@/types/chat';
import { APIResponseType } from '@/types/common';
import { MODULE_ACTIONS } from '@/utils/constant';
import Toast from '@/utils/toast';
import { useState } from 'react';

const useForkChat = () => {
    const [loading, setLoading] = useState(false);

    const createNewForkChat = async (payload: ForkChatType) => {
        try {
            setLoading(true);
            const response: APIResponseType<true> = await commonApi({
                action: MODULE_ACTIONS.FORK_CHAT,
                data: {
                    brain: { 
                        title: payload.selectedBrain.label, 
                        slug: payload.selectedBrain.slug, 
                        id: payload.selectedBrain.id,
                    },
                    title: payload.title,
                    conversation: payload.forkData,
                }
            })
            Toast(response.message);
        } catch (error) {
            console.error('error: ', error);
        } finally {
            setLoading(false);
            payload.closeModal();
        }
    }
    return {
        createNewForkChat,
        loading
    }
}

export default useForkChat