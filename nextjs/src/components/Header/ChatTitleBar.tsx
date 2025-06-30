import ChatThreadIcon from '@/icons/ChatThreadIcon';
import React from 'react';

type ChatTitleBarProps = {
    chatTitle: string;
}

const ChatTitleBar = ({ chatTitle }: ChatTitleBarProps) => {
    return (
        <div className="group hidden xl:flex items-center py-[5px] px-2.5 rounded-custom transition ease-in-out ">
            {chatTitle && (
                <>
                    <ChatThreadIcon
                        width={'16'}
                        height={'20'}
                        className="fill-b8 me-2.5"
                    />
                    <span className="text-font-14 text-b5">
                        {chatTitle.length > 100
                            ? `${chatTitle.slice(0, 100)}...`
                            : chatTitle}
                    </span>
                </>
            )}
        </div>
    );
};

export default ChatTitleBar;
