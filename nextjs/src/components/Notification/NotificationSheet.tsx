'use client'
import React, { useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
    Sheet,
    SheetClose,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
} from '@/components/ui/sheet';

import OptionsIcon from '@/icons/Options';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import useNotificationList from '@/hooks/pushNotification/useNotificationList';
import { dateDisplay, getTimeAgo } from '@/utils/common';
import UnreadNotification from './UnreadNotification';
import NotificationListLoader from '../Loader/NotificationListLoader';
import Close from '@/icons/Close';
import { useRouter } from 'next/navigation';
import routes from '@/utils/routes';
import { useSelector } from 'react-redux';
import ProfileImage from '../Profile/ProfileImage';

const NotificationSheet = ({ open, closeModal, boolean }) => {

    const { loading, notificationData, getNotificationList, removeAllNotification, markReadNotification } = useNotificationList();
    const router = useRouter();
    
    const unreadNotification = useSelector((store:any) => store.notification.unread);

    useEffect(() => {
        if (boolean) getNotificationList();
    }, [boolean])

    const handleNotificationClick = (payload) => {
        if(payload?.threadId != undefined && payload?.threadType != undefined){
            router.push(`${routes.chat}/${payload?.chatId}?mid=${payload?.messageId}&tid=${payload?.threadId}&type=${payload?.threadType}`);
        } else if(payload?.chatId != undefined){
            router.push(`${routes.chat}/${payload?.chatId}`);
        } else {
            router.push(`${routes.main}`);
        }
        
        markReadNotification({
            singleRead: true,
            notificationId: payload?._id
        });
        closeModal();        
    }
    return (
        <Sheet open={open} onOpenChange={closeModal}>
            <SheetContent>
                <SheetHeader>
                    <SheetTitle asChild>
                        <div className="flex items-center justify-between md:px-4 md:py-4 px-3 py-2">
                            <h5 className="mb-0 text-font-16 font-bold text-b2">
                                Notifications
                            </h5>
                            <div className="offcanvas-header-right ml-auto flex items-center gap-2.5">
                                <div className="mr-2">
                                    <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                            <div className="ml-auto cursor-pointer dropdown-action transparent-ghost-btn btn-round btn-round-icon [&>svg]:h-[3px] [&>svg]:w-[13px] [&>svg]:object-contain [&>svg>circle]:fill-b6">
                                                <OptionsIcon />
                                            </div>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end">
                                            <DropdownMenuItem onClick={() => markReadNotification([]) }>
                                                Mark all as read
                                            </DropdownMenuItem>
                                            <DropdownMenuItem onClick={removeAllNotification}>
                                                Delete all notifications{' '}
                                            </DropdownMenuItem>
                                        </DropdownMenuContent>
                                    </DropdownMenu>
                                </div>
                                <SheetClose asChild>
                                    <button className="w-9 h-9 rounded-full p-1 flex items-center justify-center border border-b11 hover:bg-b11">
                                        <Close width={12} height={12} className={'fill-b2 size-3 object-contain'}/>
                                    </button>
                                </SheetClose>
                            </div>
                        </div>
                    </SheetTitle>
                    <SheetDescription asChild>
                        <div>
                            <Tabs
                                defaultValue="All"
                                className="w-full px-4 h-full"
                            >
                                <TabsList className="px-0 space-x-6">
                                    <TabsTrigger className="px-0 font-medium" value="All">
                                        All 
                                        <span className='size-6 rounded-[4px] bg-b4 text-font-12 text-white leading-6 ml-1'>
                                            {notificationData.length}
                                        </span>
                                    </TabsTrigger>
                                    <TabsTrigger
                                        className="px-0 font-medium"
                                        value="Unread"
                                    >
                                        Unread 
                                        <span className='size-6 rounded-[4px] bg-red text-font-12 text-white leading-6 ml-1'>
                                                {unreadNotification.length}
                                        </span>
                                    </TabsTrigger>
                                </TabsList>
                                <TabsContent value="All" className="p-0 h-full">
                                    <div className="flex flex-1 flex-col transition ease-in-out duration-150 overflow-y-auto h-[calc(100vh-150px)] mt-5">
                                        {
                                            loading ? (
                                                [...Array(8)].map((_, index) => <NotificationListLoader key={index} />)
                                            ) : notificationData.length > 0
                                              ? notificationData.map((notification) => {
                                                return (
                                                    <div key={notification._id} onClick={() => handleNotificationClick(notification)} className="flex-shrink-0 flex border-b border-gray-200 hover:bg-b12 md:px-3 px-2 md:py-4 py-2">
                                                        <div className="size-[30px] min-w-[30px] rounded-full mr-3 relative">
                                                            <ProfileImage 
                                                                user={notification?.sender || notification.user}
                                                                w={30}
                                                                h={30}
                                                                classname={'user-img size-[30px] rounded-full mr-2.5 object-cover'}
                                                                spanclass={'bg-[#C2185B] text-b15 text-font-12 uppercase font-normal rounded-full size-[30px] min-w-5 flex items-center justify-center'}
                                                            />
                                                        </div>
                                                        <div className="text-font-15 text-b2 flex-1 text-left">
                                                            <p className='break-words'>{notification.msg}</p>
                                                            <p className="font-normal text-font-14 mt-1 text-b6">
                                                                <TooltipProvider delayDuration={0} skipDelayDuration={0}>
                                                                    <Tooltip>
                                                                        <TooltipTrigger >
                                                                            {getTimeAgo(notification.createdAt)}
                                                                        </TooltipTrigger>
                                                                        <TooltipContent side="top">
                                                                            <p>{dateDisplay(notification.createdAt, 'MMM DD [at] h:mm:ss A')}</p>
                                                                        </TooltipContent>
                                                                    </Tooltip>
                                                                </TooltipProvider>  
                                                            </p>
                                                        </div>
                                                    </div>
                                                )
                                            }): (
                                                <div className="flex flex-1 justify-center items-center text-font-16 text-gray-400 mt-5">
                                                    No record found
                                                </div>
                                            )
                                        }
                                    </div>
                                </TabsContent>
                                <UnreadNotification getTimeAgo={getTimeAgo} handleNotificationClick={handleNotificationClick} />
                            </Tabs>
                        </div>
                    </SheetDescription>
                </SheetHeader>
            </SheetContent>
        </Sheet>
    );
}
export default NotificationSheet;
