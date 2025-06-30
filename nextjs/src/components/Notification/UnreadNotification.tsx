import { dateDisplay } from '@/utils/common';
import React from 'react';
import { useSelector } from 'react-redux';
import { TabsContent } from '../ui/tabs';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '../ui/tooltip';
import ProfileImage from '../Profile/ProfileImage';

const UnreadNotification = ({handleNotificationClick, getTimeAgo}) => {
    const unreadData = useSelector((store:any) => store.notification.unread);
    return (
        <TabsContent value="Unread" className="p-0">
            <div className="flex flex-1 flex-col text-font-16 transition ease-in-out duration-150 overflow-y-auto h-[calc(100vh-150px)] mt-5">
                {
                    unreadData.length > 0 ? unreadData.map((unread) => {
                        return (
                            <div key={unread._id} onClick={() => handleNotificationClick(unread)} className="flex-shrink-0 flex border-b border-gray-200 hover:bg-b12 md:px-3 px-2 md:py-4 py-2">
                                <div className="size-[30px] rounded-full mr-3 relative">
                                    <ProfileImage
                                        user={unread?.sender || unread.user}
                                        w={30}
                                        h={30}
                                        classname={'user-img size-[30px] rounded-full mr-2.5 object-cover'}
                                        spanclass={'bg-[#C2185B] text-b15 text-font-12 uppercase font-normal rounded-full size-[30px] min-w-5 flex items-center justify-center'}
                                    />
                                    <span className="absolute top-[-2px] right-[-2px] w-[6px] h-[6px] rounded-10 bg-red"></span>
                                </div>
                                <div className="text-font-15 text-b2 flex-1 text-left">
                                    <p className='break-words'>
                                        {unread.msg}
                                    </p>
                                    <p className="font-normal text-font-14 mt-1 text-b6">
                                        <TooltipProvider
                                            delayDuration={0}
                                            skipDelayDuration={0}
                                        >
                                            <Tooltip>
                                                <TooltipTrigger>{getTimeAgo(unread.createdAt)}</TooltipTrigger>
                                                <TooltipContent side="top">
                                                    <p>{dateDisplay(unread.createdAt, 'MMM DD [at] h:mm:ss A')}</p>
                                                </TooltipContent>
                                            </Tooltip>
                                        </TooltipProvider>
                                    </p>
                                </div>
                            </div>
                        )
                    }) : (<div className="flex flex-1 justify-center items-center text-font-16 text-gray-400 mt-5"> No record found </div>)
                }
            </div>
        </TabsContent>
    );
};

export default UnreadNotification;
