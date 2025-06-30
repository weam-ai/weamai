import { formatDate, truncateText } from '@/utils/common';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import { archiveWorkspaceListAction } from '@/actions/workspace';
import DeleteAction, { ConfirmationDeleteModal } from './DeleteAction';
import UnArchiveAction from './ArchiveAction';

const ArchiveWorkspaceItem = ({ workspace }) => {
    return (
        <tr>
            <td>
                <span className="inline-flex">
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger>
                                <span>{truncateText(workspace.title, 24)}</span>
                            </TooltipTrigger>
                            <TooltipContent>
                                <p className='text-font-14'>{workspace.title}</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>


                </span>
            </td>
            <td className="text-nowrap">
                {formatDate(workspace.createdAt)}
            </td>
            <td className="text-right">
                <div className="flex items-center justify-end gap-2.5">
                    <UnArchiveAction data={workspace} btnname={'Restore Workspace'} brain={false} />
                    <DeleteAction data={workspace} btnname={'Delete Workspace'} brain={false} />
                </div>
            </td>
        </tr>
    )
}

const WorkspaceNotFound = () => {
    return (
        <tr>
            <td colSpan={3} align='center'>No Archived Workspaces</td>
        </tr>
    )
}

const ArchiveWorkspace = async () => {
    const { data } = await archiveWorkspaceListAction()
    return (
        <div className="overflow-x-auto bg-white rounded-b-10 md:max-w-[calc(100vw-55px)] max-w-[100vw">
            <table className="table rounded-b-10">
                <thead>
                    <tr className="bg-b12">
                        <th>
                            Workspace Name
                        </th>
                        <th className="text-nowrap" colSpan={2}>
                            Created Date
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {data?.length > 0 ? data.map((workspace) => (
                        <ArchiveWorkspaceItem workspace={workspace} key={workspace._id} />
                    )) : <WorkspaceNotFound />}
                </tbody>
            </table>
            <ConfirmationDeleteModal brain={false} />
        </div>
    );
}

export default ArchiveWorkspace;

// import React, { useState } from 'react';
// import ChatThreadIcon from '@/icons/ChatThreadIcon';
// import { formatDate, truncateText } from '@/utils/common';
// import UnArchiveAction from './ArchiveAction';
// import useModal from '@/hooks/common/useModal';
// import useWorkspace from '@/hooks/workspace/useWorkspace';
// import useWorkspaceList from '@/hooks/workspace/useWorkspaceList';
// import DeleteAction from './DeleteAction';
// import AlertDialogConfirmation from '@/components/AlertDialogConfirmation';
// import { getCurrentUser } from '@/utils/handleAuth';
// import { ROLE_TYPE } from '@/utils/constant';
// import {
//     Tooltip,
//     TooltipContent,
//     TooltipProvider,
//     TooltipTrigger,
// } from '@/components/ui/tooltip';


// const ArchiveWorkspace = ({ archiveWorkspace }) => {
//     const { openModal, closeModal, isOpen: isConfirmOpen } = useModal();
//     const [delWorkSpace, setDelWorkspace] = useState([]);
//     const [deleteAll, setDeleteAll] = useState(false);
//     const { hardDeleteWorkSpace, hardDeleteAllWorkSpace } = useWorkspace({ addMember: false });
//     const { restoreWorkspace } = useWorkspaceList();
    
//     const handleDeleteBrain = () => {
//         const currentUser = getCurrentUser();
//         const companyId = (currentUser.roleCode === ROLE_TYPE.COMPANY) ? currentUser.company.id : currentUser.invitedBy;

//         if(deleteAll){
//             hardDeleteAllWorkSpace(closeModal, companyId);
//             setDeleteAll(false);
//         } else {
//             hardDeleteWorkSpace('', delWorkSpace?.slug, delWorkSpace?._id, closeModal);
//         }
//         closeModal();
//     };

//     const restore = (payload) => {
//         restoreWorkspace(payload);
//     }

//     return (
//         <div className="overflow-x-auto bg-white rounded-b-10 max-w-[calc(100vw-55px)] ">
//             <table className="table rounded-b-10">
//                 <thead>
//                     <tr className="bg-b12">
//                         <th>
//                             Workspace Name
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
//                                     <button onClick={() => { openModal(); setDeleteAll(true); }}>
//                                         Delete All Workspace
//                                     </button>
//                                     </DropdownMenuItem>
//                                 </DropdownMenuContent>
//                             </DropdownMenu> */}
//                         </th>
//                     </tr>
//                 </thead>
//                 <tbody>
//                     {archiveWorkspace.map((workspace) => (
//                         <tr key={workspace._id}>
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
//                                                 <span>{truncateText(workspace.title,24)}</span>
//                                             </TooltipTrigger>
//                                             <TooltipContent>
//                                                 <p className='text-font-14'>{workspace.title}</p>
//                                             </TooltipContent>
//                                         </Tooltip>       
//                                     </TooltipProvider>

                                    
//                                 </span>
//                             </td>
//                             <td className="text-nowrap">
//                                 {formatDate(workspace.createdAt)}
//                             </td>
//                             <td className="text-right">
//                                 <div className="flex items-center justify-end gap-2.5">
//                                     <UnArchiveAction data={workspace} restore={restore} btnname={'Restore Workspace'} />
//                                     <DeleteAction data={workspace} openModal={openModal} setDelBrain={setDelWorkspace} btnname={'Delete Workspace'} />
//                                 </div>
//                             </td>
//                         </tr>
//                     ))}
//                     { archiveWorkspace.length == 0 &&
//                         <tr>
//                             <td colSpan={3} align='center'>No Archived Workspaces</td>
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
//                     id={delWorkSpace}
//                 />
//             )}
//         </div>
//     );
// }

// export default ArchiveWorkspace;
