import { createSlice } from '@reduxjs/toolkit';

const customgptSlice = createSlice({
    name: 'customgpt',
    initialState: {
        basic: {},
        aimodal: {},
        doc: {},
    },
    reducers: {
        setCustomGptBasicAction: (state, action) => {
            state.basic = action.payload;
        },
        setCustomGptAIModalAction: (state, action) => {
            state.basic = action.payload;
        },
        setCustomGptDocAction: (state, action) => {
            state.basic = action.payload;
        },
    },
});

export const {
    setCustomGptAIModalAction,
    setCustomGptBasicAction,
    setCustomGptDocAction,
} = customgptSlice.actions;

export default customgptSlice.reducer;
