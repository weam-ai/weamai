import { ObjectType } from '@/types/common';
import { SelectedWorkSpaceType, WorkspaceListType } from '@/types/workspace';
import { createSlice } from '@reduxjs/toolkit';

type WorkSpaceSlice = {
    list: WorkspaceListType[],
    modalSts?: boolean,
    selected: SelectedWorkSpaceType,
    loading: boolean,
    archivelist: ObjectType[]
}

const initialState: WorkSpaceSlice = {
    list: [],
    modalSts: false,
    selected: null,
    loading: false,
    archivelist: []
}

const workspacelist = createSlice({
    name: 'workspacelist',
    initialState,
    reducers: {
        setWorkSpaceListAction: (state, action) => {
            state.list = action.payload
        },
        setArchiveWorkSpace: (state, action) => {
            state.archivelist = action.payload
        },
        addWorkspaceListAction: (state, action) => {
            state.list.unshift(action.payload)
        },
        editWorkspaceListAction: (state:any, action) => {
            const updatedList = state.list.map(item => {
                if (item._id === action.payload._id) {
                  return { ...action.payload }; 
                }
                return item;
              });
              state.list = updatedList;
              if(state.selected._id == action.payload._id){
                state.selected = action.payload
              }
        },
        setWorkspaceModalStatus: (state, action) => {
            state.modalSts = action.payload
        },
        setSelectedWorkSpaceAction: (state, action) => {
            state.selected = action.payload
        },
        setWorkspaceLoading: (state, action) => {
            state.loading = action.payload;
        }
    },
});

export const { addWorkspaceListAction, editWorkspaceListAction, setWorkspaceModalStatus, setWorkSpaceListAction, setSelectedWorkSpaceAction, setWorkspaceLoading, setArchiveWorkSpace  } = workspacelist.actions;

export default workspacelist.reducer;
