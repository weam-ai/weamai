'use client';
import useChat from '@/hooks/chat/useChat';
import { createHandleOutsideClick, dateDisplay } from '@/utils/common';
import Link from 'next/link';
import React, { useEffect, useState,useRef, useMemo, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { LINK } from '@/config/config';
import routes from '@/utils/routes';
import { chatMemberListAction } from '@/lib/slices/chat/chatSlice';
import { useSearchParams } from 'next/navigation';
import CheckIcon from '@/icons/CheckIcon';
import AlertDialogConfirmation from '../AlertDialogConfirmation';
import useModal from '@/hooks/common/useModal';
import { getCurrentUser } from '@/utils/handleAuth';
import { ROLE_TYPE } from '@/utils/constant';
import ProfileImage from '../Profile/ProfileImage';
import ActionSuggestion from '../Shared/ActionSuggestion';
import RemoveIcon from '@/icons/RemoveIcon';
import PencilIcon from '@/icons/PencilIcon';
import { ChatListType } from '@/types/chat';
import SearchBar from '@/widgets/SearchBar';
import ChatListSkeleton from '../Loader/ChatList';
import BookMarkIcon, { ActiveBookMark } from '@/icons/Bookmark';
import useChatMember from '@/hooks/chat/useChatMember';
import { LoadMorePagination } from '../Shared/PaginationControl';
import useSearch from '@/hooks/common/useSearch';
import { encodedObjectId, isUserNameComplete } from '@/utils/helper';
import NoResultFound from '../NoResult/NoResultFound';
import { useRouter } from 'next/navigation';


const ChatItem = () => {
    const searchParams = useSearchParams();
    const brainId = searchParams.get('b');
    const { chatList, getAllChatList, editChat, deleteChat, isLoading, paginator,
        showFavorites, setShowFavorites
    , setChatList } = useChat(brainId);
    const { openModal, closeModal, isOpen: isConfirmOpen } = useModal();
    const router = useRouter();
    const [isEditing, setIsEditing] = useState(false);
    const [editedTitles, setEditedTitles] = useState(false);
    const [editItemId, setEditItemId] = useState(null);
    const [deleteItem, setDeleteItem] = useState({});

    const dispatch = useDispatch();

    const chatNameInputRef=useRef(null);
    const chatNameButtonRef=useRef(null)

    const { searchValue, setSearchValue } = useSearch({
        func: getAllChatList,
        delay: 500,
        dependency: [brainId],
        resetState: () => setChatList([])
    });

    const { favouriteChat } = useChatMember();
    const handleEditClick = (chatId: string, currentTitle: string) => {
        setIsEditing((prevState) => ({
            ...prevState,
            [chatId]: true, // Set editing flag for this chat item
        }));
        setEditedTitles((prevState) => ({
            ...prevState,
            [chatId]: currentTitle, // Initialize edited title with current title
        }));
    };

    const handleTitleChange = (event: React.ChangeEvent<HTMLInputElement>, chatId: string) => {
        const { value } = event.target;
        setEditedTitles((prevState) => ({
            ...prevState,
            [chatId]: value, // Update edited title for this chat item
        }));
    };



    const handleSaveClick = (chatId: string) => {
        editChat(chatId, {
            title: editedTitles[chatId],
        });
        setEditItemId(null); // Reset edit mode after saving
        // setEditedTitles(false); //if we make edited titles false on save older title show first after new title appears
        setIsEditing(false);
    };

    const handleDeleteChat = () => {
        deleteChat(deleteItem._id, deleteItem.chatId._id);
        closeModal();
        setDeleteItem({});
    };

   const handlePagination = useCallback(() => {
        if(paginator?.hasNextPage) {
            getAllChatList(searchValue, { offset: paginator.offset + paginator.perPage, limit: paginator.perPage });
        }
    }, [paginator]);

    const userDetail = useMemo(() => getCurrentUser(), []);
    useEffect(() => {
        if(!isUserNameComplete(userDetail)){
            router.push(routes.onboard);   
            return;
        }
    }, [userDetail]);
    
    useEffect(() => {
        dispatch(chatMemberListAction([]));
    }, [brainId]);


    useEffect(
        () => {

            if(!isEditing) return 

            const handleClickOutside = createHandleOutsideClick(
                chatNameInputRef,
                chatNameButtonRef,
                setIsEditing,
                setEditedTitles,
                false,
                false
            );

            document.addEventListener('mousedown', handleClickOutside);

            return () =>
                document.removeEventListener('mousedown', handleClickOutside);
        },
        [isEditing,setIsEditing]
    );
    const [bookmarkStates, setBookmarkStates] = useState({});
    const [favLoading, setFavLoading] = useState(false);
    const handleBookmark = async (isFavourite, chatId) => {
        setFavLoading(true);
        setBookmarkStates(prev => ({
            ...prev,
            [chatId]: isFavourite
        }));

        await favouriteChat(isFavourite, chatId);
        if (!isFavourite && showFavorites) {
            setChatList((prevList) => prevList.filter(chat => chat.chatId._id !== chatId));
        }
        setFavLoading(false);
    };
    
    const isFirstRender = useRef(true);

    useEffect(() => {
        if (isFirstRender.current) {
            isFirstRender.current = false;
            return;
        }
        getAllChatList(searchValue);
    }, [showFavorites]);

    return (
        <>
            <SearchBar
                placeholder={'Search Chats'}
                btnname={'Start a Chat'}
                searchValue={searchValue}
                setSearchValue={setSearchValue}
                setShowFavorites={setShowFavorites}
                showFavorites={showFavorites}
            />
            {
                chatList.length > 0 && 
                <div className="relative xl:flex justify-between gap-2.5 w-full max-w-[950px] mx-auto px-5 mb-2 hidden">
                    <div className="w-full lg:w-3/5 pr-4">
                        <p className="text-font-16 font-semibold text-b2">
                            Name
                        </p>
                    </div>
                    <div className="w-full lg:w-2/5 flex items-center ">
                        <p className="text-font-16 font-semibold text-b2">
                            Owner
                        </p>
                    </div>
                </div>
                    
            }
            

            <div className="h-full overflow-y-auto w-full relative pb-16">
                <div className="chat-items max-w-[950px] mx-auto px-5 grid grid-cols-1 gap-2.5">
                    {chatList.length > 0 && chatList.map((chat: ChatListType) => {
                        
                        const isCurrentlyEditing = isEditing[chat.chatId?._id];
                        const editedTitle =
                            editedTitles[chat.chatId?._id] || chat.chatId?.title;
                        const { user } = chat.chatId;
                        
                        return (
                            <React.Fragment key={`${chat._id}-${chat.chatId?._id}`}>
                                <div
                                    className={
                                        `${!isCurrentlyEditing ? 'md:hover:bg-b2' : ''} group/item bg-gray-100 border rounded-custom md:hover:bg-b5 pl-5 pr-2.5 w-full transition duration-150 ease-in-out` 
                                    }
                                >
                                    <div className="relative flex md:justify-between justify-start gap-2.5 w-full items-center md:flex-nowrap flex-wrap">
                                        <div className="w-full">
                                            <Link
                                                href={
                                                    isCurrentlyEditing
                                                        ? '#'
                                                        : `${LINK.DOMAIN_URL}${routes.chat}/${chat.chatId._id}?b=${encodedObjectId(chat.brain.id)}`
                                                }
                                            >
                                                <div className="flex w-full py-4 flex-col xl:flex-row break-all">
                                                    <div className="w-full flex xl:w-3/5 pr-4 mb-2 xl:mb-0">
                                                        {isCurrentlyEditing ? (
                                                            <input
                                                                type="text"
                                                                ref={chatNameInputRef}
                                                                className="flex-1 mr-3 p-0 m-0 border md:group-hover/item:text-white border-b2 focus:border-b2 px-2 outline-none bg-transparent rounded-custom text-font-14 font-semibold leading-[19px] text-b2"
                                                                value={editedTitle}
                                                                onChange={(event) =>
                                                                    handleTitleChange(
                                                                        event,
                                                                        chat.chatId?._id
                                                                    )
                                                                }
                                                                autoFocus
                                                                maxLength={50}
                                                            />
                                                        ) : (
                                                            <p className="text-font-14 font-normal text-b2 md:group-hover/item:text-b15">
                                                                {chat?.chatId?.title === undefined ? 'New Chat' : chat.chatId?.title!==editedTitle && editedTitles ? editedTitle :chat.chatId?.title}
                                                            </p>
                                                        )}
                                                        {isCurrentlyEditing ? (
                                                            <button
                                                                type="button"
                                                                ref={chatNameButtonRef}
                                                                className="edit-title md:group-hover/item:bg-white transparent-ghost-btn btn-round btn-round-icon"
                                                                onClick={() =>{
                                                                   
                                                                    if(chat.chatId.title!==editedTitle){
                                                                        handleSaveClick(
                                                                            chat.chatId
                                                                                ?._id
                                                                        )
                                                                    }else{
                                                                        setIsEditing(false)
                                                                    }
                                                                }
                                                                }
                                                            >
                                                                <CheckIcon className="size-4 object-contain fill-b6" />
                                                            </button>
                                                        ) : null}
                                                    </div>

                                                    <div className="w-full lg:w-2/5 flex items-center ">
                                                        <ProfileImage user={user} w={10} h={10}
                                                            classname={'user-img size-5 rounded-full mr-2.5 object-cover'}
                                                            spanclass={'bg-[#C2185B] text-b15 text-font-12 uppercase font-normal rounded-full w-5 h-5 min-w-5 flex items-center justify-center'}
                                                        />
                                                        <ul className="flex *:px-2.5 flex-col lg:flex-row">
                                                            <li className="text-font-12 text-b5 relative md:group-hover/item:text-b15 md:after:content-[''] md:after:absolute md:after:w-[3px] md:after:h-[3px] md:after:rounded-full after:bg-b7 after:top-1/2 after:right-0 after:-translate-y-1/2 group-hover/item:after:bg-b15 last:after:hidden">
                                                                {`${user.fname} ${user.lname}` || user.email.split('@')[0]}
                                                            </li>
                                                            <li className="text-font-12 text-b5 relative md:group-hover/item:text-b15 md:after:content-[''] md:after:absolute md:after:w-[3px] md:after:h-[3px] md:after:rounded-full after:bg-b7 after:top-1/2 after:right-0 after:-translate-y-1/2 group-hover/item:after:bg-b15 last:after:hidden">
                                                                {dateDisplay(
                                                                    chat?.chatId?.createdAt || chat?.createdAt
                                                                )}
                                                            </li>
                                                        </ul>
                                                    </div>
                                                </div>
                                            </Link>
                                        </div>
                                        {
                                            ((userDetail.roleCode === ROLE_TYPE.USER && chat.chatId.user.id === userDetail._id) ||
                                                userDetail.roleCode !== ROLE_TYPE.USER) && (
                                                    <>
                                                    <Link
                                                        href={'#'}
                                                        onClick={() => {
                                                            openModal();
                                                            setDeleteItem(chat);
                                                        }}
                                                        className="md:group-hover/item:opacity-100 md:opacity-0 rounded md:bg-white bg-b11 md:mb-0 mb-2 flex items-center justify-center w-6 min-w-6 h-6 p-0.5 [&>svg]:w-[11] [&>svg]:h-[11] [&>svg]:fill-b5"
                                                    >
                                                        <RemoveIcon width={14} height={14} className='fill-b5' />
                                                    </Link>
                                                    <Link
                                                        href={'#'}
                                                        onClick={() => {
                                                            handleEditClick(
                                                                chat.chatId?._id,
                                                                chat.chatId.title
                                                            )
                                                        }}
                                                        className="md:group-hover/item:opacity-100 md:opacity-0 rounded md:bg-white bg-b11 md:mb-0 mb-2 flex items-center justify-center w-6 min-w-6 h-6 p-0.5 [&>svg]:w-[11] [&>svg]:h-[11] [&>svg]:fill-b5"
                                                    >
                                                        <PencilIcon width={11} height={11}/>
                                                    </Link>
                                                    
                                                    </>
                                                
                                            )
                                        }
                                        <Link href={'#'}
                                            onClick={() => {
                                                const isFavourite = bookmarkStates[chat.chatId._id] ?? chat?.isFavourite ? false : true;
                                                !favLoading && handleBookmark(isFavourite, chat.chatId?._id);
                                            }}
                                            className="md:group-hover/item:opacity-100 md:opacity-0 rounded md:bg-white bg-b11 md:mb-0 mb-2 flex items-center justify-center w-6 min-w-6 h-6 p-0.5 cursor-pointer hidden12"
                                            >
                                            {bookmarkStates[chat.chatId?._id] ?? chat?.isFavourite ? (
                                                <ActiveBookMark width={15} height={14} className="fill-orange" />
                                            ) : (
                                                <BookMarkIcon width={15} height={14} className="fill-b5" />
                                            )}
                                        </Link>
                                    </div>
                                </div>
                            </React.Fragment>
                        );
                    })}
                    {isLoading && <ChatListSkeleton items={10}/>}
                    {
                        chatList.length === 0 && !isLoading && !showFavorites && !searchValue &&
                            <ActionSuggestion
                            title="No Chats Found Yet? Let's Get You Started!"
                            description="No worries—getting started is easy! Watch this quick demo to learn how to start using AI-powered chats with your team.
                                        Collaborate smarter with real-time AI and team chats, save and share important conversations, and streamline work with AI for ideas, research, and task automation."
                            subtitle="Ready to start your first chat?" 
                            note="Click 'Start Chat' above to begin a conversation."
                            videourl="https://www.youtube.com/embed/V5jrXsK0Za0?si=0rhca6n7PHwT-042"
                            />
                    }
                    {
                        searchValue && chatList.length === 0 && !isLoading && !showFavorites &&
                            <NoResultFound message="Search results not found." />
                    }
                    {
                        chatList.length === 0 && !isLoading && showFavorites && 
                            <NoResultFound message="You haven't added any chats to your Favorites yet." />
                    }
                </div>
                <LoadMorePagination
                    paginator={paginator}
                    handlePagination={handlePagination}
                    isLoading={isLoading}
                />
                {isConfirmOpen && (
                    <AlertDialogConfirmation
                        description={
                            `Are you sure you want to delete ${deleteItem?.chatId?.title ? ` ${deleteItem.chatId.title}` : ''}?`
                        }
                        btntext={'Sure'}
                        btnclassName={'btn-red'}
                        open={openModal}
                        closeModal={closeModal}
                        handleDelete={handleDeleteChat}
                        id={deleteItem?._id}
                    />
                )}
            </div>
        </>
    );
};

export default React.memo(ChatItem);