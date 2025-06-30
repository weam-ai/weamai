'use client';

import dynamic from 'next/dynamic';
const DocumentItems = dynamic(() => import('./DocumentItems'), { ssr: false });

export const DocumentItemsWrapper = () => {
    return <DocumentItems />;
};