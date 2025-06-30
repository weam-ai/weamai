'use client';
import dynamic from 'next/dynamic';
const PromptItems = dynamic(() => import('./PromptItems'), { ssr: false });

export const PromptItemsWrapper = () => {
    return <PromptItems />;
};