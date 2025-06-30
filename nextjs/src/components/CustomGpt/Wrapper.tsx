'use client';
import dynamic from 'next/dynamic';
const AgentList = dynamic(() => import('./AgentList'), { ssr: false });
const AddAgent = dynamic(() => import('./AddAgent'), { ssr: false });
const EditAgent = dynamic(() => import('./EditAgent'), { ssr: false });
export const AgentListWrapper = () => {
    return <AgentList />;
};

export const AddAgentWrapper = () => {
    return <AddAgent />;
};

export const EditAgentWrapper = () => {
    return <EditAgent />;
};