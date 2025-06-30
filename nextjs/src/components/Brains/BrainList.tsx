'use client';
import ChatIcon from '@/icons/Chat';
import Customgpt from '@/icons/Customgpt';
import LeftTriangle from '@/icons/LeftTriangle';
import PromptIcon from '@/icons/Prompt';
import routes from '@/utils/routes';
import Link from 'next/link';
import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { useSidebar } from '@/context/SidebarContext';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import RenameIcon from '@/icons/RenameIcon';
import RemoveIcon from '@/icons/RemoveIcon';
import OptionsIcon from '@/icons/Options';
import CheckIcon from '@/icons/CheckIcon';
import Plus from '@/icons/Plus';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
import {
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from '../ui/accordion';
import { decodedObjectId, encodedObjectId, persistBrainData } from '@/utils/helper';
import { setEditBrainModalAction } from '@/lib/slices/modalSlice';
import DocumentIcon from '@/icons/DocumentIcon';
import { AI_MODEL_CODE, GENERAL_BRAIN_SLUG, ROLE_TYPE } from '@/utils/constant';
import { SettingsIcon } from '@/icons/SettingsIcon';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { createHandleOutsideClick, truncateText } from '@/utils/common';
import useServerAction from '@/hooks/common/useServerActions';
import { deleteBrainAction, updateBrainAction } from '@/actions/brains';
import { setSelectedBrain } from '@/lib/slices/brain/brainlist';
import Toast from '@/utils/toast';
import { BrainListType } from '@/types/brain';
import { setLastConversationDataAction, setUploadDataAction } from '@/lib/slices/aimodel/conversation';
import { SetUserData } from '@/types/user';
import { chatMemberListAction } from '@/lib/slices/chat/chatSlice';

type DefaultEditOptionProps = {
    onEdit: () => void;
    handleEditBrain: () => void;
    handleDeleteBrain: () => void;
    isDeletePending: boolean;
}

type CommonListProps = {
    b: BrainListType;
    isprivate?: boolean;
    currentUser: SetUserData;
}

type DefaultListOptionProps = {
    brain: BrainListType;
    isprivate?: boolean;
}

type LinkItemsProps = {
    icon: React.ReactNode;
    text: string;
    href: string;
    data: BrainListType;
}

export const matchedBrain = (brains: BrainListType[], brainId: string) => {
    return brains?.find((brain) => brain._id === brainId);
}

const LinkItems = React.memo(({ icon, text, href, data }: LinkItemsProps) => {
    const originalPath = href;
    if (data?.slug !== undefined) href = `${href}?b=${encodedObjectId(data?._id)}`;
    let pathname = usePathname();
    const searchParams = useSearchParams();
    const router = useRouter();
    const dispatch = useDispatch();
    const { closeSidebar } = useSidebar();
    const brainId = searchParams.get('b') ? decodedObjectId(searchParams.get('b')) : null;
    if (pathname.includes("/chat/") && brainId === data?._id) {
        pathname = "/chat";
    }

    const isActive = useMemo(
        () => (data?._id === brainId && originalPath === pathname),
        [data?._id, brainId, originalPath, pathname]
    );

    const handleNewChatClick = useCallback(() => {
        const b = encodedObjectId(data?._id);
        dispatch(setUploadDataAction([]));
        dispatch(setLastConversationDataAction({}));
        dispatch(chatMemberListAction([]));
        closeSidebar();
        router.push(`${routes.main}?b=${b}&model=${AI_MODEL_CODE.DEFAULT_OPENAI_SELECTED}`);
    }, [brainId, closeSidebar]);
    const handleLinkClick = () => {
        // Close the sidebar on link click
        closeSidebar();
    };
    
    return (
        <li className="relative group">
            {text === 'Chats' && (
                <TooltipProvider delayDuration={0} skipDelayDuration={0}>
                    <Tooltip>
                        <TooltipTrigger
                            asChild
                            className="peer absolute right-2.5 top-2 ms-auto size-5 flex items-center justify-center outline-none bg-b15 rounded-full transition ease-in-out opacity-0 invisible group-hover:opacity-100 group-hover:visible"
                        >
                            <button
                                onClick={handleNewChatClick}
                            >
                                <Plus
                                    width={'10'}
                                    height={'10'}
                                    className="fill-b5"
                                />
                            </button>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>New Chat</p>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
            )}
            <Link
                href={href}
                className={`${
                    isActive ? 'active' : ''
                } peer-hover:bg-blue5 flex items-center px-[15px] py-[8.6px] text-b5 rounded-custom hover:text-blue [&.active]:text-blue`}
                onClick={handleLinkClick}
            >
                <span
                    className={`${
                        isActive ? 'active' : ''
                    } mr-2.5 [&>svg]:h-4 [&>svg]:w-4 [&>svg]:fill-b6 group-hover:[&>svg]:fill-blue [&>svg]:[&.active]:fill-blue`}
                >
                    {icon}
                </span>
                <span className="inline-block me-2">{text}</span>
            </Link>
        </li>
    );
});

const DefaultListOption = React.memo(({ brain } : DefaultListOptionProps) => {
    const listOptions = [
        {
            icon: <ChatIcon />,
            text: 'Chats',
            id: 1,
            href: routes.chat,
            data: brain,
        },
        {
            icon: (
                <PromptIcon
                    width={'16'}
                    height={'16'}
                    className="size-4 object-contain"
                />
            ),
            text: 'Prompts',
            id: 2,
            href: routes.prompts,
            data: brain,
        },
        {
            icon: (
                <Customgpt
                    width={'16'}
                    height={'16'}
                    className="size-4 object-contain"
                />
            ),
            text: 'Agents',
            id: 3,
            href: routes.customGPT,
            data: brain,
        },
        {
            icon: (
                <DocumentIcon
                    width={16}
                    height={16}
                    className="size-4 object-contain"
                />
            ),
            text: 'Docs',
            id: 4,
            href: routes.docs,
            data: brain,
        },
    ];

    return listOptions.map((list) => (
        <LinkItems
            key={list.id}
            icon={list.icon}
            text={list.text}
            href={list.href}
            data={list.data}
        />
    ));
});

const DefaultEditOption = React.memo(
    ({ onEdit, handleEditBrain, handleDeleteBrain, isDeletePending }: DefaultEditOptionProps) => {
        return (
            <DropdownMenu>
                <DropdownMenuTrigger asChild>
                    <div className="ml-auto md:opacity-0 group-hover:opacity-100 dropdown-action transparent-ghost-btn btn-round btn-round-icon [&>svg]:h-[3px] [&>svg]:w-[13px] [&>svg]:object-contain [&>svg>circle]:fill-b6 data-[state=open]:opacity-100">
                        <OptionsIcon />
                    </div>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="min-w-[210px] !rounded-[15px]">
                    <DropdownMenuItem
                        className="edit-collapse-title border-0"
                        onClick={onEdit}
                    >
                        <RenameIcon
                            width={14}
                            height={16}
                            className="w-[14] h-4 object-contain fill-b4 me-2.5"
                        />
                        Rename
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={handleDeleteBrain} disabled={isDeletePending} className="border-0">
                        <RemoveIcon
                            width={14}
                            height={16}
                            className="w-[14] h-4 object-contain fill-b4 me-2.5"
                        />
                        Archive
                    </DropdownMenuItem>
                    <DropdownMenuItem
                        className="edit-collapse-title"
                        onClick={handleEditBrain}
                    >
                        
                        <SettingsIcon width={14}
                            height={16} className="w-[14] h-4 object-contain fill-b4 me-2.5" />
                        Manage
                    </DropdownMenuItem>
                </DropdownMenuContent>
            </DropdownMenu>
        );
    }
);

export const CommonList = ({ b, isprivate, currentUser }: CommonListProps) => {
    
    const dispatch = useDispatch();

    // Editable Menu start
    const [isEditing, setIsEditing] = useState(false);
    const [editedTitle, setEditedTitle] = useState(b.title);
    const inputRef = useRef(null);
    const buttonRef=useRef(null)
    const [deleteBrain, isDeletePending] = useServerAction(deleteBrainAction);
    const [updateBrain, isUpdatePending] = useServerAction(updateBrainAction);

    const searchParams = useSearchParams();
    const brainId = searchParams.get('b') ? decodedObjectId(searchParams.get('b')) : null;

    const isActive = useMemo(
        () => (b?._id === brainId),
        [b?._id, brainId]
    );

    const handleEditClick = () => {
        setIsEditing(true);
        setEditedTitle(b.title); // Reset editedTitle to the current title
    };

    useEffect(() => {

        if(!isEditing) return;

       const handleClickOutside=createHandleOutsideClick(inputRef,buttonRef,setIsEditing,false,setEditedTitle,b.title)
      
        document.addEventListener('mousedown', handleClickOutside);
       
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isEditing,setIsEditing,setEditedTitle]);

    useEffect(() => {
        if (isEditing && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isEditing]);


    const handleSaveClick = async () => {
        if(b.title !==inputRef.current.value){
            const payload = {
                title: editedTitle,
                isShare: b?.isShare,
                workspaceId: b?.workspaceId
            };

            const response:any=await updateBrain(payload, b?._id);

            if(response?.code=='ERROR'){
                setEditedTitle(b?.title)
            }
            setIsEditing(false)
            Toast(response?.message);
        }
    };

    const handleInputChange = (e) => {
        setEditedTitle(e.target.value);
    };
    // Editable Menu end

    const handleEditBrain = (w) => {
        dispatch(
            setEditBrainModalAction({
                open: true,
                brain: w,
            })
        );
    };

    const handleDeleteBrain = async (brain) => {
        const data = {
            isShare: brain.isShare,
        };
        const response = await deleteBrain(data, brain?._id);
        Toast(response?.message);
    };

    return (
        <>
            <AccordionItem value={b.title} key={b._id} className="border-0">
                <AccordionTrigger
                    className={`${isActive ? 'active' : ''} group relative flex w-full items-center py-1.5 px-2 text-left transition [overflow-anchor:none] hover:z-[2] focus:z-[3] focus:outline-none [&>span>.accordion-icon]:hidden rounded-custom [&.active]:bg-b12`}
                >
                    <span className="triangle-icon mr-[5px] h-2.5 w-2.5 shrink-0 rotate-0 transition-transform duration-200 ease-in-out motion-reduce:transition-none [&>svg]:h-2.5 [&>svg]:w-2.5 [&>svg]:fill-b6 [&>svg]:object-contain">
                        <LeftTriangle />
                    </span>
                    {isEditing ? (
                        <input
                            type="text"
                            ref={inputRef}
                            className="flex-1 mr-3 p-0 m-0 border border-blue outline-none bg-transparent rounded-custom text-font-14 font-semibold leading-[19px] text-b2 focus:border-blue"
                            value={editedTitle}
                            onChange={handleInputChange}
                            maxLength={50}
                            autoFocus
                        />
                    ) : (
                        <span className="collapse-editable-title flex-1 text-font-14 font-medium leading-[19px]">
                            {b.title!==editedTitle ? truncateText(editedTitle,29) : truncateText(b.title,29)}
                        </span>
                    )}
                    {isEditing ? (
                        <button
                            type="button"
                            className="edit-title transparent-ghost-btn btn-round btn-round-icon"
                            onClick={handleSaveClick}
                            ref={buttonRef}
                            disabled={isUpdatePending}
                        >
                            <CheckIcon className="size-4 object-contain fill-b6" />
                        </button>
                    ) : null}
                    {                                                
                    (b?.slug != `default-brain-${currentUser?._id}` && b?.slug !== GENERAL_BRAIN_SLUG && ((currentUser?.roleCode === ROLE_TYPE.USER && b.user.id === currentUser?._id) ||
                    currentUser?.roleCode !== ROLE_TYPE.USER))  && (
                        <DefaultEditOption
                            onEdit={handleEditClick}
                            handleEditBrain={() => handleEditBrain(b)}
                            handleDeleteBrain={() => handleDeleteBrain(b)}
                            isDeletePending={isDeletePending}
                        />
                    )}
                </AccordionTrigger>
                <AccordionContent className="pt-1">
                    <ul className="flex flex-col *:text-font-14 *:leading-[1.2] *:text-b2" onClick={() => {
                        persistBrainData(b)
                        dispatch(setSelectedBrain(b))
                    }}>
                        <DefaultListOption brain={b} isprivate={isprivate} />
                    </ul>
                </AccordionContent>
            </AccordionItem>
        </>
    );
};