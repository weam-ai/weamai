import React from 'react';

type ChatListSkeletonProps = {
    items: number;
}

const ChatListSkeleton: React.FC<ChatListSkeletonProps> = ({ items }) => {
    return (
        <div className="space-y-4">
            {Array.from({ length: items }).map((_, index) => (
                <div
                    key={index}
                    className="animate-pulse flex items-center justify-between p-4 bg-gray-200 rounded-md flex-wrap md:flex-nowrap"
                >
                    <div className="flex items-center space-x-4 w-full md:w-[45%] md:mb-0 mb-2">
                        <div className="w-full h-3 bg-gray-300 rounded"></div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <div className="w-6 h-6 bg-gray-300 rounded-full"></div>
                        <div className="w-20 h-3 bg-gray-300 rounded"></div>
                        <div className="w-16 h-3 bg-gray-300 rounded"></div>
                    </div>
                    <div className="flex items-center space-x-2">
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ChatListSkeleton;