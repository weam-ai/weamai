import { ChatRefineActionPayloadType, ConversationType } from '@/types/chat';
import {  createSlice } from '@reduxjs/toolkit';
import { CreditInfoType } from '@/types/user';
type initialStateType = {
    members: any[];
    favourite: boolean;
    addMemberModal: boolean;
    thread: any;
    isOpenThreadModal: boolean;
    chatAccess: boolean;
    canvasOptions: ChatRefineActionPayloadType;
    creditInfo: CreditInfoType;
    initialMessage: ConversationType;
}

const initialState:initialStateType = {
    members: [],
    favourite: false,
    addMemberModal: false,
    thread: {},
    isOpenThreadModal: false,
    chatAccess: false,
    canvasOptions: {} as ChatRefineActionPayloadType,
    initialMessage: {} as ConversationType,
    creditInfo: {} as CreditInfoType,
}
const chatSlice = createSlice({
    name: 'chat',
    initialState: initialState,
    reducers: {
        chatMemberListAction: (state, action) => {
            state.members = action.payload
        },
        addChatMemberAction: (state, action) => {
            state.members.unshift(action.payload)
        },
        setFavouriteAction: (state, action) => {
            state.favourite = action.payload
        },
        setAddMemberModalAction: (state, action) => {
            state.addMemberModal = action.payload;
        },
        setIsOpenThreadModalAction: (state, action) => {
            state.isOpenThreadModal = action.payload;
        },
        setThreadAction: (state, action) => {
            state.thread = action.payload;
        },
        setListThreadAction: (state, action) => {
            if (state.thread?.messageId == action.payload?.messageId && state.thread?.type == action.payload?.type) {
                state.thread = {
                    ...state.thread,
                    data: [...state.thread.data, ...action.payload.data]
                }
            }
        },
        setAddThreadAction: (state, action) => {
            if (state.thread?.messageId == action.payload?.messageId && state.thread?.type == action.payload?.type) {
                state.thread = {
                    ...state.thread,
                    data: [...state.thread.data, action.payload]
                }
            }
        },
        setUpdateThreadAction: (state, action) => {
            const index = action.payload.index;
            const updatedItems = [...state.thread.data];
            updatedItems[index] = action.payload;
            state.thread = {
                ...state.thread,
                data: updatedItems
            }
        },
        setChatAccessAction: (state, action) => {
            state.chatAccess = action.payload
        },
        setCanvasOptionAction: (state, action) => {
            state.canvasOptions = action.payload;
        },
        setChatInfoAction: (state:any, action:any) => {
            state.chatInfo = action.payload;
        },
        setCreditInfoAction: (state, action) => {
            state.creditInfo = action.payload;
        },
        setInitialMessageAction: (state, action) => {
            state.initialMessage = action.payload;
        }
    }
})

export const {
    chatMemberListAction,
    addChatMemberAction,
    setFavouriteAction,
    setAddMemberModalAction,
    setIsOpenThreadModalAction,
    setThreadAction,
    setAddThreadAction,
    setUpdateThreadAction,
    setListThreadAction,
    setChatAccessAction,
    setCanvasOptionAction,
    setChatInfoAction,
    setCreditInfoAction,
    setInitialMessageAction,
} = chatSlice.actions;

export default chatSlice.reducer;