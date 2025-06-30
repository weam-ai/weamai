import { createSlice } from '@reduxjs/toolkit';

const aiModal = createSlice({
    name: 'aiModal',
    initialState: {
        list: [],
        addTitle: true,
        inputKey: false,
        selectedValue: {},
        updatetitle: false,
        cleartitle: false,
        visible: true, // show dropdown option and input field
        message: false,
        modalData: {}
    },
    reducers: {
        cacheModalList: (state, action) => {
            state.list = action.payload;
        },
        setAddTitle: (state, action) => {
            state.addTitle = action.payload;
        },
        setInputStatus: (state, action) => {
            state.inputKey = action.payload;
        },
        setSelectedValue: (state, action) => {
            state.selectedValue = action.payload;
        },
        setUpdateTitle: (state, action) => {
            state.updatetitle = action.payload;
        },
        setClearTitle: (state, action) => {
            state.cleartitle = action.payload;
        },
        setVisibleAction: (state, action) => {
            state.visible = action.payload
        },
        setMessageAction: (state, action) => {
            state.message = action.payload
        },
        setModalData: (state, action) => {
            state.modalData = action.payload
        }
    },
});

export const {
    cacheModalList,
    setAddTitle,
    setInputStatus,
    setSelectedValue,
    setUpdateTitle,
    setClearTitle,
    setVisibleAction,
    setMessageAction,
    setModalData
} = aiModal.actions;

export default aiModal.reducer;
