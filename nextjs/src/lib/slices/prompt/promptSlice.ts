import { BrainPromptType } from '@/types/brain';
import { PaginatorType } from '@/types/common';
import { createSlice } from '@reduxjs/toolkit';
type InitialStateType = {
    list: BrainPromptType[];
    paginator: PaginatorType;
    modalSts: boolean;
}

const initialState: InitialStateType = {
    list: [],
    paginator: {} as PaginatorType,
    modalSts: false
}

const promptSlice = createSlice({
    name: 'prompt',
    initialState,
    reducers: {
        setPromptlistAction: (state, action) => { 
            state.list = action.payload;
        },
        setPromptPaginator: (state, action) => {
            state.paginator = action.payload;            
        },
        setAddNewPromptAction: (state, action) => {
            state.list.unshift(action.payload);
        }
    },
});

export const { setPromptlistAction, setPromptPaginator, setAddNewPromptAction } = promptSlice.actions;

export default promptSlice.reducer;
