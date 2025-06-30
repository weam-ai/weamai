import { formatDate, truncateText } from '@/utils/common';
import { UnArchiveActionWrapper } from './Wrapper';
import DeleteAction, { ConfirmationDeleteModal } from './DeleteAction';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import { archiveBrainAction } from '@/actions/brains';

const ArchiveBrainNotFound = () => {
    return (
        <tr>
            <td colSpan={5} align='center'>No Archived Brains</td>
        </tr>
    )
}

const ArchiveBrainItem = ({ brain }) => {
    return (
        <tr>
            <td>
                <span className="inline-flex min-w-48">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger className='text-left'>
                                <span>{truncateText(brain.title, 19)}</span>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p className='text-font-14'>{brain.title}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                </span>
            </td>
            <td className="text-nowrap">
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger>
                            <span>{truncateText(brain?.workspaceId?.title, 19)}</span>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p className='text-font-14'>{brain?.workspaceId?.title}</p>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            </td>
            <td className="text-nowrap">
                {brain?.user?.fname} {brain?.user?.lname}
            </td>
            <td className="text-nowrap">
                {formatDate(brain.createdAt)}
            </td>
            <td className="text-right">
                <div className="flex items-center justify-end gap-2.5">
                    <UnArchiveActionWrapper data={brain} btnname={'Restore Brain'} />
                    <DeleteAction data={brain} btnname={'Delete Brain'} />
                </div>
            </td>
        </tr>
    )
}

const ArchiveBrain = async () => {
    const { data } = await archiveBrainAction();

    return (
        <div className="overflow-x-auto bg-white rounded-b-10 md:max-w-[calc(100vw-55px)] max-w-[100vw]">
            <table className="table rounded-b-10">
                <thead>
                    <tr className="bg-b12">
                        <th>
                            Brain Name
                        </th>
                        <th className="text-nowrap">
                            Workspace
                        </th>
                        <th className="text-nowrap">
                            Created By
                        </th>
                        <th className="text-nowrap" colSpan={2}>
                            Created Date
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {data?.length > 0 ? data.map((brain) => (
                        <ArchiveBrainItem brain={brain} key={brain._id} />
                    )) : <ArchiveBrainNotFound />}
                </tbody>
            </table>
            <ConfirmationDeleteModal />
        </div>
    );
}

export default ArchiveBrain;

// import React, { useState } from 'react';
// import ChatThreadIcon from '@/icons/ChatThreadIcon';
// import { formatDate, truncateText } from '@/utils/common';
// import useModal from '@/hooks/common/useModal';
// import AlertDialogConfirmation from '@/components/AlertDialogConfirmation';
// import useBrains from '@/hooks/brains/useBrains';
// import UnArchiveAction from './ArchiveAction';
// import DeleteAction from './DeleteAction';
// import {
//     Tooltip,
//     TooltipContent,
//     TooltipProvider,
//     TooltipTrigger,
// } from '@/components/ui/tooltip';

// const ArchiveBrain = ({ archiveBrainList }) => {
//     const { openModal, closeModal, isOpen: isConfirmOpen } = useModal();
//     const [delBrain, setDelBrain] = useState([]);
//     const [deleteAll, setDeleteAll] = useState(false);
//     const { hardDeleteBrain, restoreBrain, hardDeleteAllBrain } = useBrains({
//         isShare: false,
//         addMember: false,
//     });
    
//     const handleDeleteBrain = () => {
        
//         if(deleteAll){
//             setDeleteAll(false);
//             hardDeleteAllBrain(closeModal);
//         } else {
//             const data = {
//                 isShare: delBrain.isShare,
//             };

//             hardDeleteBrain(data, delBrain?.slug, delBrain?._id, closeModal);            
//         }
//     };

//     const restore = (payload) => {
//         restoreBrain(payload);
//     }

//     return (
//         <div className="overflow-x-auto bg-white rounded-b-10 max-w-[calc(100vw-55px)]">
//             <table className="table rounded-b-10">
//                 <thead>
//                     <tr className="bg-b12">
//                         <th>
//                             Brain Name
//                         </th>
//                         <th className="text-nowrap">
//                             Workspace
//                         </th>
//                         <th className="text-nowrap">
//                             Created By
//                         </th>
//                         <th className="text-nowrap">
//                             Created Date
//                         </th>
//                         <th className="text-right">
//                             {/* <DropdownMenu>
//                                 <DropdownMenuTrigger className="ml-auto flex justify-center items-center [&>svg]:h-[3px] [&>svg]:w-[13px] [&>svg]:object-contain [&>svg>circle]:fill-b6 w-[25px] h-[25px] min-w-[25px] rounded-full transition duration-150 ease-in-out hover:bg-b11 focus:bg-b11 active:bg-b11">
//                                     <OptionsIcon />
//                                 </DropdownMenuTrigger>
//                                 <DropdownMenuContent align="end">
//                                     <DropdownMenuItem className="text-reddark">
//                                         <button onClick={() => { openModal(); setDeleteAll(true); }}>
//                                             Delete All Brain
//                                         </button>
//                                     </DropdownMenuItem>
//                                 </DropdownMenuContent>
//                             </DropdownMenu> */}
//                         </th>
//                     </tr>
//                 </thead>
//                 <tbody>
//                     {archiveBrainList.map((brain) => (
//                         <tr key={brain._id}>
//                             <td>
//                                 <span className="inline-flex">
//                                     <ChatThreadIcon
//                                         width="16"
//                                         height="16"
//                                         className="w-4 min-w-4 h-4 object-contain mt-1 fill-b7 inline-block me-2.5"
//                                     />
//                                     <TooltipProvider>
//                                         <Tooltip>
//                                             <TooltipTrigger>
//                                                 <span>{truncateText(brain.title, 19)}</span>
//                                             </TooltipTrigger>
//                                             <TooltipContent>
//                                                 <p className='text-font-14'>{brain.title}</p>
//                                             </TooltipContent>
//                                         </Tooltip>
//                                     </TooltipProvider>
//                                 </span>
//                             </td>
//                             <td className="text-nowrap">
//                                 <TooltipProvider>
//                                     <Tooltip>
//                                         <TooltipTrigger>
//                                             <span>{truncateText(brain?.workspaceId?.title, 19)}</span>
//                                         </TooltipTrigger>
//                                         <TooltipContent>
//                                             <p className='text-font-14'>{brain?.workspaceId?.title}</p>
//                                         </TooltipContent>
//                                     </Tooltip>
//                                 </TooltipProvider>
//                             </td>
//                             <td className="text-nowrap">
//                                 {brain?.user?.fname} {brain?.user?.lname}
//                             </td>
//                             <td className="text-nowrap">
//                                 {formatDate(brain.createdAt)}
//                             </td>
//                             <td className="text-right">
//                                 <div className="flex items-center justify-end gap-2.5">
//                                     <UnArchiveAction data={brain} restore={restore} btnname={'Restore Brain'} />
//                                     <DeleteAction data={brain} openModal={openModal} setDelBrain={setDelBrain} btnname={'Delete Brain'} />                                    
//                                 </div>
//                             </td>
//                         </tr>
//                     ))}
//                     { archiveBrainList.length == 0 &&
//                         <tr>
//                             <td colSpan={5} align='center'>No Archived Brains</td>
//                         </tr>
//                     }
//                 </tbody>
//             </table>
//             {isConfirmOpen && (
//                 <AlertDialogConfirmation
//                     description={
//                         'Are you sure you want to delete ?'
//                     }
//                     btntext={'Delete'}
//                     btnclassName={'btn-red'}
//                     open={openModal}
//                     closeModal={closeModal}
//                     handleDelete={handleDeleteBrain}
//                     id={delBrain}
//                 />
//             )}
//         </div>
//     );
// }

// export default ArchiveBrain;