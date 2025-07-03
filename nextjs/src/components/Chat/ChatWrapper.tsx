'use client';
import dynamic from 'next/dynamic';

const ChatAccessControl = dynamic(
    () => import('@/components/Chat/ChatClone'),
    {
        ssr: false,
    }
);

const ChatItem = dynamic(
    () => import('@/components/Chat/ChatItem'),
    {
        ssr: false,
    }
);

const RefreshTokenClient = dynamic(
    () => import('@/components/Shared/RefreshTokenClient'),
    {
        ssr: false,
    }
);
const HomeChatInput = dynamic(
    () => import('@/components/Chat/ChatInput'),
    {
        ssr: false,
    }
);

const HomeAiModel = dynamic(
    () => import('@/components/Header/HomeAiModel'),
    {
        ssr: false,
    }
);


export const ChatCloneWrapper = () => {
    return <ChatAccessControl />;
};

export const ChatItemWrapper = () => {
    return <ChatItem />;
};

export const RefreshTokenClientWrapper = () => {
    return <RefreshTokenClient />;
};

export const HomeChatInputWrapper = ({ aiModals }) => {
    return <HomeChatInput aiModals={aiModals} />;
};

export const HomeAiModelWrapper = ({ aiModals }) => {
    return <HomeAiModel aiModals={aiModals} />;
};