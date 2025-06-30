import { AiModalType } from '@/types/aimodels';
import { API_TYPE_OPTIONS } from '@/utils/constant';
import { createSlice } from '@reduxjs/toolkit';


type initialStateType = {
    list: AiModalType[];
    selectedModal: AiModalType;
    isWebSearchActive: boolean;
}


const initialState:initialStateType = {
    list: [],
    selectedModal: {} as AiModalType,
    isWebSearchActive: false,
}

const assignModelSlice = createSlice({
    name: 'assignmodel',
    initialState: initialState,
    reducers: {
        assignModelListAction: (state, action) => {
            state.list = action.payload;
        },
        addNewAssignModelAction: (state, action) => {
            state.list.unshift(action.payload);
        },
        setSelectedAIModal: (state, action) => {
            state.selectedModal = action.payload;
            if(action.payload.bot.code == API_TYPE_OPTIONS.PERPLEXITY){
                state.isWebSearchActive = true;
            }else{
                state.isWebSearchActive = false;
            }
        },
        setIsWebSearchActive: (state, action) => {
            state.isWebSearchActive = action.payload;
        },
    },
});

export const {
    addNewAssignModelAction,
    assignModelListAction,
    setSelectedAIModal,
    setIsWebSearchActive,
} = assignModelSlice.actions;

export default assignModelSlice.reducer;
