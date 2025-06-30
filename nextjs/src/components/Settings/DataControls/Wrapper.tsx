'use client';

import dynamic from 'next/dynamic';
const UnArchiveAction = dynamic(() => import('./ArchiveAction'), { ssr: false });

export const UnArchiveActionWrapper = ({ data, btnname, brain = true }) => {
    return <UnArchiveAction data={data} btnname={btnname} brain={brain} />;
};
