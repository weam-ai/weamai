'use client';

import ShareIcon, { ShareIcon2 } from '@/icons/Share';
import CopyIcon from '@/icons/CopyIcon';
import LinkIcon from '@/icons/LinkIcon';
import Label from '@/widgets/Label';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { useSelector, useDispatch } from 'react-redux';
import { setShareModalAction } from '@/lib/slices/modalSlice';
import { useEffect, Fragment, useState } from 'react';
import { useParams } from 'next/navigation';
import useConversation from '@/hooks/conversation/useConversation';
import useShareChat from '@/hooks/chat/useShareChat';
import { retrieveBrainData } from '@/utils/helper';
import { LINK } from '@/config/config';
import { copyToClipboard } from '@/utils/common';
import ThreeDotLoader from '../Loader/ThreeDotLoader';

export const ShareModal = () => {
    const dispatch = useDispatch();
    const handleCancel = () => {
        dispatch(setShareModalAction(false));
    }; 
    const handleOpen = () => {
        dispatch(setShareModalAction(true));
    };

    const params = useParams();

    const { getAllConversation, conversations, responseLoading } = useConversation();
    const { loading, createShareChat } = useShareChat();
    const [chatAccess, setChatAccess] = useState(1);
    const [chatLink, setChatLink] = useState(`${LINK.DOMAIN_URL}/public/chat/${params.id}`);

    const handlePublicClick = () => {
        setChatAccess(1);
        setChatLink(`${LINK.DOMAIN_URL}/public/chat/${params.id}`);
    };

    const handleCreateShareChat = () => {
        const braindata = retrieveBrainData();
        createShareChat({
            brainId: braindata._id,
            chatId: params.id,
            access: chatAccess,
            uri: chatLink,
            conversation: conversations,
        });
        dispatch(setShareModalAction(false));
    };

    useEffect(() => {
        getAllConversation({ chatId: params.id });
    }, []);

    return (
        <>
            <Dialog open={handleOpen} onOpenChange={handleCancel}>
                <DialogContent className="md:max-w-[680px] max-w-[calc(100%-30px)] py-8">
                    <DialogHeader className="rounded-t-10 px-[30px] pb-5 border-b">
                        <DialogTitle className="font-semibold flex items-center">
                            <ShareIcon2 width={24} height={(24 * 22) / 25} className="w-6 h-auto object-contain fill-b2 me-3 inline-block align-text-top" />
                            Share this Chat
                        </DialogTitle>
                    </DialogHeader>

                    <div className="dialog-body flex flex-col flex-1 relative h-full overflow-hidden px-[30px]">
                        <div className="h-full pt-6">
                            <Label
                                title={'Chat Link:'}
                                htmlFor={'label'}
                                required={false}
                                Icon={LinkIcon}
                                IconWidth={20}
                                IconHeight={20}
                                IconClassName="fill-b1 inline mr-3 mb-1"
                            />
                            <div className="relative">
                                {responseLoading === false ? (
                                    <>
                                        <input
                                            readOnly
                                            type="text"
                                            value={chatLink}
                                            name="searchgpt"
                                            id="searchgpt"
                                            className="default-form-input mt-3 bg-gray-200"
                                        />
                                        <span
                                            onClick={() => {
                                                copyToClipboard(chatLink);
                                                handlePublicClick();
                                                handleCreateShareChat();
                                            }}
                                            className='absolute right-2 top-position bg-b10 cursor-pointer flex items-center justify-center w-8 h-8 rounded-custom p-1.5 transition ease-in-out duration-150 hover:bg-b9 dark:hover:bg-w12'
                                        >
                                            <CopyIcon
                                                width={'16'}
                                                height={'16'}
                                                className='h-[18px] w-auto max-w-full fill-black dark:fill-w6'
                                            />
                                        </span>
                                    </>
                                ) : (
                                    <ThreeDotLoader />
                                )}
                            </div>

                            <div className="small-description text-font-14 leading-[24px] text-b5 font-normal mt-5">
                                <p>
                                    {`Messages you send after creating your link won't
                                be shared. Anyone with the URL will be able to
                                view the shared chat.`}
                                </p>
                            </div>                            
                        </div>
                    </div>
                </DialogContent>
            </Dialog>
        </>
    );
};

const Share = () => {
    const isOpen = useSelector((store:any) => store.modalSlice.shareModal);
    const dispatch = useDispatch();
    const handleOpen = () => {
        dispatch(setShareModalAction(true));
    };
    return (
        <>
        <TooltipProvider>
        <Tooltip>
            <TooltipTrigger asChild>
                <div>
                    <button type="button"
                        className="w-9 lg:w-10 h-9 lg:h-10 lg:min-w-10 rounded-full p-2 flex items-center justify-center border border-b11 hover:bg-b11 [&>svg]:fill-b2 [&>svg]:fill-h-4 [&>svg]:w-4 [&>svg]:object-contain overflow-hidden"
                        onClick={handleOpen}
                    >
                        <ShareIcon width={40} height={40} className="w-10 h-auto" />
                    </button>
                    {isOpen && <ShareModal />}
                </div>
            </TooltipTrigger>
            <TooltipContent>
            <p className='text-font-14'>Share this Chat</p>
            </TooltipContent>
        </Tooltip>
        </TooltipProvider>

            
            
        </>
    );
};

export default Share;