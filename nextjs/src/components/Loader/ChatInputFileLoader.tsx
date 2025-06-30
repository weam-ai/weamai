import React from 'react';

const ChatInputFileLoader = () => {
    return (
        <div className="px-5 mt-2">
            <span className="flex items-end">
                <span className="text-font-14 text-b5">Uploading</span>
                <span className="flex ml-1 space-x-1 mb-1">
                    <span className="w-1 h-1 bg-b5 rounded-full animate-[blink_1.4s_ease-in-out_infinite]"></span>
                    <span className="w-1 h-1 bg-b5 rounded-full animate-[blink_1.4s_ease-in-out_infinite_0.2s]"></span>
                    <span className="w-1 h-1 bg-b5 rounded-full animate-[blink_1.4s_ease-in-out_infinite_0.4s]"></span>
                </span>
            </span>
        </div>
    );
};

export default ChatInputFileLoader;
