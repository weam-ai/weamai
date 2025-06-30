import React from 'react';
import {
    Dialog,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogClose,
} from '@/components/ui/dialog';
import WorkSpaceIcon from '@/icons/WorkSpaceIcon';
import SearchIcon from '@/icons/Search';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import OptionsVerticalIcon from '@/icons/OptionsVerticalIcon';
import { useDispatch, useSelector } from 'react-redux';
import { setWorkpaceModalAction } from '@/lib/slices/modalSlice';

const MemberWorkspaceListModal = ({ open, closeModal }) => {
    const isWorkspaceModal = useSelector(
        (store:any) => store.modalSlice.workspaceModal
    );
    const dispatch = useDispatch();
    const handleClose = () => {
        dispatch(setWorkpaceModalAction(false));
    };
    return (
        <Dialog open={isWorkspaceModal} onOpenChange={handleClose}>
            <DialogContent className="md:max-w-[600px] max-w-[calc(100%-30px)]">
                <DialogHeader>
                    <DialogTitle className="rounded-t-10 text-font-18 font-bold text-b2 bg-b12 px-[30px] py-6 border-b borer-b11">
                        <WorkSpaceIcon className="w-6 h-6 min-w-6 object-contain fill-b2 me-4 inline-block align-text-top" />
                        Harry Jack -{' '}
                        <span className="font-normal">Workspaces</span>
                    </DialogTitle>
                </DialogHeader>
                <div className="dialog-body overflow-y-auto h-full max-h-[80vh] pt-5 pb-7">
                    {/* Search Start */}
                    <div className="search-wrap search-member relative mx-[30px] mb-4">
                        <input
                            type="text"
                            className="default-form-input default-form-input-border-light default-form-input-md !text-font-16"
                            id="searchMember"
                            placeholder="Search Member"
                        />
                        <span className="inline-block absolute left-[15px] top-1/2 -translate-y-1/2 [&>svg]:fill-b7">
                            <SearchIcon className="w-4 h-[17px] fill-b7" />
                        </span>
                    </div>
                    {/* Search End */}
                    <ul role="list" className="divide-y divide-b11 *:px-[30px]">
                        <li className="flex items-center justify-between py-2.5 group/item relative">
                            <span className="text-b2 text-font-16">
                                ChatMinds AI
                            </span>
                            <span>
                                <DropdownMenu>
                                    <DropdownMenuTrigger className="transparent-ghost-btn btn-round btn-round-icon">
                                        <OptionsVerticalIcon />
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                        <DropdownMenuItem className="text-reddark">
                                            Remove Workspace
                                        </DropdownMenuItem>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            </span>
                        </li>
                        <li className="flex items-center justify-between py-2.5 group/item relative">
                            <span className="text-b2 text-font-16">
                                ChatMinds AI
                            </span>
                            <span className="flex space-x-2.5">
                                <span className="bg-b11 py-1 px-4 text-font-14 font-normal text-b3 inline-block rounded-10">
                                    Admin
                                </span>
                                <DropdownMenu>
                                    <DropdownMenuTrigger className="transparent-ghost-btn btn-round btn-round-icon">
                                        <OptionsVerticalIcon />
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                        <DropdownMenuItem className="text-reddark">
                                            Remove Workspace
                                        </DropdownMenuItem>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            </span>
                        </li>
                        <li className="flex items-center justify-between py-2.5 group/item relative">
                            <span className="text-b2 text-font-16">
                                ChatMinds AI
                            </span>
                            <span>
                                <DropdownMenu>
                                    <DropdownMenuTrigger className="transparent-ghost-btn btn-round btn-round-icon">
                                        <OptionsVerticalIcon />
                                    </DropdownMenuTrigger>
                                    <DropdownMenuContent align="end">
                                        <DropdownMenuItem className="text-reddark">
                                            Remove Workspace
                                        </DropdownMenuItem>
                                    </DropdownMenuContent>
                                </DropdownMenu>
                            </span>
                        </li>
                    </ul>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default MemberWorkspaceListModal;
