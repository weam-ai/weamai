'use client'
import NotificationIcon from '@/icons/NotificationIcon';
import React, { use } from 'react';
import useModal from '@/hooks/common/useModal';
import NotificationSheet from '../Notification/NotificationSheet';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
function Notification() {
    const { isOpen, openModal, closeModal } = useModal();
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                <span className='relative w-10 h-10 flex items-center justify-center rounded-full cursor-pointer ease-in-out duration-150 bg-transparent hover:bg-b5 hover:bg-opacity-[0.2] [&.active]:bg-white [&.active]:bg-opacity-[0.1]'>
                    <NotificationIcon
                        width={'18'}
                        height={'18'}
                        className="w-[18px] h-auto object-contain fill-b2"
                        onClick={() => {
                            openModal();
                        }}
                    />
                    {isOpen && (
                        <NotificationSheet
                            open={openModal}
                            closeModal={closeModal}
                            boolean={isOpen}
                        />
                    )}
                </span>
                </TooltipTrigger>
                <TooltipContent side="top" className="border-none">
                <p className='text-font-14'>Notifications</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
        
    );
}

export default Notification;
