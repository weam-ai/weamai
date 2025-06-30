'use client';
import { setModalStatus } from '@/lib/slices/brain/brainlist';
import { setEditBrainModalAction, setEditWorkpaceModalAction } from '@/lib/slices/modalSlice';
import { setWorkspaceModalStatus } from '@/lib/slices/workspace/workspacelist';
import { useDispatch, useSelector } from 'react-redux';
import BrainModal from '../Brains/BrainModal';
import AddWorkspaceModal from '../Workspace/WorkspaceModal';
import EditWorkSpaceModal from '../Workspace/EditWorkSpaceModal';
import EditBrainModal from '../Brains/EditBrainModal';

export const ModelOptions = () => {
    const isPrivate = useSelector((store:any) => store.brain.brainMode);
    const isBrainModalOpen = useSelector((store:any) => store.brain.modalSts);
    const isWorkspaceModalOpen = useSelector((store:any) => store.workspacelist.modalSts);

    const { open: isEditModal, workspace } = useSelector((store:any) => store.modalSlice.editWorkspaceModal);
    const { open: isBrainEditModal, brain } = useSelector((store:any) => store.modalSlice.editBrainModal);

    const dispatch = useDispatch();

    const closeBrainModal = () => {
        dispatch(setModalStatus(false));
    };

    const closeWorkspaceModal = () => {
        dispatch(setWorkspaceModalStatus(false));
    };

    const closeEditWorkspaceModal = () => {
        dispatch(
            setEditWorkpaceModalAction({
                open: false,
            })
        );
    };

    const closeEditBrainModal = () => {
        dispatch(
            setEditBrainModalAction({
                open: false,
            })
        );
    };

    return (
        <>
            {isBrainModalOpen && (
                <BrainModal
                    open={isBrainModalOpen}
                    close={closeBrainModal}
                    isPrivate={isPrivate}
                />
            )}
            {isWorkspaceModalOpen && (
                <AddWorkspaceModal
                    open={isWorkspaceModalOpen}
                    close={closeWorkspaceModal}
                />
            )}
            {isEditModal && (
                <EditWorkSpaceModal
                    open={isEditModal}
                    workspace={workspace}
                    closeModal={closeEditWorkspaceModal}
                />
            )}
            {isBrainEditModal && (
                <EditBrainModal
                    open={isBrainEditModal}
                    brain={brain}
                    closeModal={closeEditBrainModal}
                />
            )}
        </>
    );
};