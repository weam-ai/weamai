import { BrainListType } from '@/types/brain';
import { createSlice } from '@reduxjs/toolkit';

type InitialStateType = {
    shareList: BrainListType[];
    privateList: BrainListType[];
    brainMode: boolean;
    modalSts: boolean;
    combined: BrainListType[];
    selectedBrain: BrainListType;
    archiveBrains: BrainListType[];
    archiveSelectedId: string | null;
}

const initialState: InitialStateType = {
    shareList: [],
    privateList: [],
    brainMode: false,
    modalSts: false,
    combined: [],
    selectedBrain: {} as BrainListType,
    archiveBrains: [],
    archiveSelectedId: null
}

const brain = createSlice({
    name: 'brain',
    initialState,
    reducers: {
        cacheShareList: (state, action) => {
            state.shareList = action.payload;
            state.combined = [...state.privateList, ...action.payload];
        },
        cachePrivateList: (state, action) => {
            state.privateList = action.payload;
            state.combined = [...action.payload, ...state.shareList];
        },
        archiveBrainList: (state, action) => {
            state.archiveBrains = action.payload;
        },
        addToShareList: (state, action) => {
            // state.shareList.unshift(action.payload);
            const { type, payload } = action.payload;

            switch (type) {
                case 'update':
                    state.shareList = payload;
                    break;
                case 'delete':
                    state.shareList = payload;
                    break;
                default:
                    state.shareList.unshift(payload);
            }  
        },
        addToPrivateList: (state, action) => {
            const { type, payload } = action.payload;

            switch (type) {
                case 'update':
                    state.privateList = payload;
                    break;
                case 'delete':
                    state.privateList = payload;
                    break;
                default:
                    state.privateList.unshift(payload);
            }            
        },
        setToPrivateBrain: (state, action) => {
            state.brainMode = action.payload
        },
        setModalStatus: (state, action) => {
            state.modalSts = action.payload
        },
        setSelectedBrain: (state, action) => {
            state.selectedBrain = action.payload
        },
        setArchiveSelectedId: (state, action) => {
            state.archiveSelectedId = action.payload
        }
    },
});

export const {
    cachePrivateList,
    cacheShareList,
    addToPrivateList,
    addToShareList,
    setToPrivateBrain,
    setModalStatus,
    setSelectedBrain,
    archiveBrainList,
    setArchiveSelectedId
} = brain.actions;

export default brain.reducer;
