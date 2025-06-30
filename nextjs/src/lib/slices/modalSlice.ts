import { createSlice } from "@reduxjs/toolkit";

const modalSlice = createSlice({
    name: 'modalSlice',
    initialState: {
        workspaceModal: false,
        editWorkspaceModal : {},
        editBrainModal : {},
        brainModal: false,
        inviteMemberModal: false,
        requestDetailsModal: false,
        addAiModel: false,
        shareModal: false,
        promptModal: false,
        notificationsheet: false,
        movetobrainmodal: false,
        confirmationDeleteModal: false,
    },
    reducers: {
        setWorkpaceModalAction: (state, action) => {
            state.workspaceModal = action.payload;
        },
        setEditWorkpaceModalAction: (state, action) => {
            state.editWorkspaceModal = action.payload;
        },
        setBrainModalAction: (state, action) => {
            state.brainModal = action.payload;
        },
        setEditBrainModalAction: (state, action) => {
            state.editBrainModal = action.payload;
        },
        setInviteMemberModalAction: (state, action) => {
            state.inviteMemberModal = action.payload;
        },
        setRequestDetailsModalAction: (state, action) => {
            state.requestDetailsModal = action.payload;
        },
        setAddAiModalAction: (state, action) => {
            state.addAiModel = action.payload;
        },
        setNotificationAction: (state, action) => {
            state.notificationsheet = action.payload;
        },
        setShareModalAction: (state, action) => {
            state.shareModal = action.payload;
        },
        setPromptModalAction: (state, action) => {
            state.promptModal = action.payload;
        },
        setMovetoBrainModalAction: (state, action) => {
            state.movetobrainmodal = action.payload;
        },
        setConfirmationDeleteModalAction: (state, action) => {
            state.confirmationDeleteModal = action.payload;
        }

    }
})

export const {
    setBrainModalAction, 
    setWorkpaceModalAction,
    setInviteMemberModalAction,
    setRequestDetailsModalAction,
    setAddAiModalAction,
    setShareModalAction,
    setPromptModalAction,
    setEditWorkpaceModalAction,
    setEditBrainModalAction,
    setNotificationAction,
    setMovetoBrainModalAction,
    setConfirmationDeleteModalAction
} = modalSlice.actions

export default modalSlice.reducer
