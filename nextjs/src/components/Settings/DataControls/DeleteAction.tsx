'use client';
import { hardDeleteBrainAction } from '@/actions/brains';
import { hardDeleteWorkspaceAction } from '@/actions/workspace';
import AlertDialogConfirmation from '@/components/AlertDialogConfirmation';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import useServerAction from '@/hooks/common/useServerActions';
import RemoveIcon from '@/icons/RemoveIcon';
import { setArchiveSelectedId } from '@/lib/slices/brain/brainlist';
import { setConfirmationDeleteModalAction } from '@/lib/slices/modalSlice';
import { RootState } from '@/lib/store';
import Toast from '@/utils/toast';
import { useDispatch, useSelector } from 'react-redux';

const DeleteAction = ({ data, btnname, brain = true }) => {
    const dispatch = useDispatch();
    const handleDelete = () => {
        dispatch(setConfirmationDeleteModalAction(true));
        if (brain) {
            dispatch(setArchiveSelectedId(data._id));
        } else {
            dispatch(setArchiveSelectedId(data.slug));
        }
    }
    return (
        <TooltipProvider delayDuration={0} skipDelayDuration={0}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <button onClick={handleDelete}>
                        <RemoveIcon
                            width={18}
                            height={18}
                            className={
                                'w-[18px] h-[18px] object-contain fill-b7 hover:fill-b2'
                            }
                        />
                    </button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                    <p>{btnname}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};

export const ConfirmationDeleteModal = ({ brain = true }) => {
    const confirmationDeleteModal = useSelector((state:RootState) => state.modalSlice.confirmationDeleteModal);
    const archiveSelectedId = useSelector((state:RootState) => state.brain.archiveSelectedId);
    const [hardDeleteBrain, loading] = useServerAction(hardDeleteBrainAction);
    const [hardDeleteWorkspace, loadingWorkspace] = useServerAction(hardDeleteWorkspaceAction);
    const dispatch = useDispatch();
    const closeModal = () => {
        dispatch(setConfirmationDeleteModalAction(false));
        dispatch(setArchiveSelectedId(null));
    }
    const handleDelete = async () => {
        if (brain) {
            const response = await hardDeleteBrain(archiveSelectedId);
            Toast(response.message);
            closeModal();
        } else {
            const response = await hardDeleteWorkspace(archiveSelectedId);
            Toast(response.message);
            closeModal();
        }
    }
    return (
        confirmationDeleteModal && (
            <AlertDialogConfirmation
                description={'Are you sure you want to delete ?'}
                btntext={'Delete'}
                btnclassName={'btn-red'}
                open={confirmationDeleteModal}
                closeModal={closeModal}
                handleDelete={handleDelete}
                loading={loading || loadingWorkspace}
            />
        )
    )
}

export default DeleteAction;

// import {
//     Tooltip,
//     TooltipContent,
//     TooltipProvider,
//     TooltipTrigger,
// } from '@/components/ui/tooltip';
// import RemoveIcon from '@/icons/RemoveIcon';

// const DeleteAction = ({data, openModal, setDelBrain, btnname}) => {
//     return (
//         <TooltipProvider delayDuration={0} skipDelayDuration={0}>
//             <Tooltip>
//                 <TooltipTrigger asChild>
//                     <button onClick={() => { openModal(); setDelBrain(data); }}>
//                         <RemoveIcon
//                             width={16}
//                             height={16}
//                             className={
//                                 'w-[16px] h-[16px] object-contain fill-b4 hover:fill-red'
//                             }
//                         />
//                     </button>
//                 </TooltipTrigger>
//                 <TooltipContent side="bottom">
//                     <p>{btnname}</p>
//                 </TooltipContent>
//             </Tooltip>
//         </TooltipProvider>
//     );
// };

// export default DeleteAction;