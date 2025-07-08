import commonApi from '@/api';
import {  setListThreadAction } from '@/lib/slices/chat/chatSlice';
import {  MODULES, MODULE_ACTIONS } from '@/utils/constant';
import { useState } from 'react';
import { useDispatch } from 'react-redux';
const useThread = () => {
    const [isLoading, setIsLoading] = useState(false);
    const dispatch = useDispatch();
    
    const addNewThread = async (nextIndex, payload) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.CREATE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.REPLAY_THREAD,
                common: true,
                data: payload,
            })
            return response.data;
        } catch (error) {
            console.log('error: ', error);
        }
    }

    const getListReplyThread = async (payload) => {
        try {
            setIsLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.REPLAY_THREAD,
                common: true,
                data: {
                    options: {
                        sort: { createdAt: 1 },
                        pagination: false,
                        populate: [
                            {
                                path: 'sender',
                                select: 'profile email fname lname'
                            }
                        ]
                    },
                    query: { 'messageId': payload.messageId, type: payload.type }
                }
            })
            dispatch(setListThreadAction({
                messageId:payload.messageId,
                type: payload.type,
                data: response.data
            }));
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setIsLoading(false);
        }
    }

    return { addNewThread, getListReplyThread, isLoading };
};

export default useThread;
