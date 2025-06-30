import { UploadedFileType } from '@/types/chat';
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

type LastConversationType = {
    responseModel?: string;
    responseAPI?: string;
    customGptId?: string;
}

type InitialStateType = {
    setTitle: boolean;
    chatTitle: string;
    uploadData: UploadedFileType[];
    lastConversation: LastConversationType;
}

const initialState: InitialStateType = {
    setTitle: true,
    chatTitle: '',
    uploadData: [],
    lastConversation: {} as LastConversationType
}

const conversationSlice = createSlice({
    name: 'conversation',
    initialState,
    reducers: {
        setChatTitleMessageAction: (state: InitialStateType, action: PayloadAction<boolean>) => {
            state.setTitle = action.payload
        },
        setChatMessageAction: (state: InitialStateType, action: PayloadAction<string>) => {
            state.chatTitle = action.payload
        },
        setUploadDataAction: (state: InitialStateType, action: PayloadAction<UploadedFileType[]>) => {
            state.uploadData = action.payload
        },
        setLastConversationDataAction: (state: InitialStateType, action: PayloadAction<LastConversationType>) => {
            state.lastConversation = action.payload
        },
    },
});

export const { setChatTitleMessageAction, setChatMessageAction, setUploadDataAction, setLastConversationDataAction } = conversationSlice.actions;

export default conversationSlice.reducer;
