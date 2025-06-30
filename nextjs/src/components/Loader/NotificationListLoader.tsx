import React from 'react';

const NotificationListLoader = () => {
    return (
        <div className="flex-shrink-0 flex px-3 py-4 w-full animate-pulse">
            <div className="size-[30px] rounded-full bg-gray-400 mr-3 relative"></div>
            <div className="flex-1">
                <div className="h-4 bg-gray-300 w-full rounded-custom"></div>
                <div className="h-4 bg-gray-300 mt-1 w-full rounded-custom"></div>
                <div className="h-4 bg-gray-300 w-1/2 mt-3 rounded-custom"></div>
            </div>
        </div>
    );
};

export default NotificationListLoader;
