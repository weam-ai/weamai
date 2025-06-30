import React from 'react';

type AgentListSkeletonProps = {
    items: number;
}

const AgentListSkeleton: React.FC<AgentListSkeletonProps> = ({ items }) => {
    return (
        <div className="space-y-4">
            {Array.from({ length: items }).map((_, index) => (
                <div
                    key={index}
                    className="animate-pulse flex items-center justify-between p-4 bg-gray-200 rounded-md gap-5"
                >
                        <div className="w-10 h-10 bg-gray-300 rounded"></div>
                        <div className="flex flex-col space-y-2 w-full">
                            <div className="w-24 h-4 bg-gray-300 rounded"></div>
                            <div className="w-[95%] h-4 bg-gray-300 rounded"></div>
                        </div>
                </div>
            ))}
        </div>
    );
};

export default AgentListSkeleton;