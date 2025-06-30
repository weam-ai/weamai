'use client';

import useNotificationList from '@/hooks/pushNotification/useNotificationList';
import React, { useEffect } from 'react'

const NotificationDot = () => {
    const { unreadNotificationCount, unreadcount } = useNotificationList();
    useEffect(() => {
        unreadNotificationCount();
    }, []);
    return (
        <>
            {unreadcount > 0 &&
                <span className="absolute bottom-auto left-auto right-2.5 top-1.5 z-10 inline-block rounded-full bg-red w-1.5 h-1.5"></span>
            }
        </>
    )
}

export default NotificationDot