import React from 'react';

type AgentGridSkeletonProps = {
    items: number;
}

const AgentGridSkeleton: React.FC<AgentGridSkeletonProps> = ({ items }) => {
    return (
        <div className="gap-4 prompts-items-grid grid lg:grid-cols-3 grid-cols-2 lg:gap-5 max-w-[950px] mx-auto w-full col-span-3">
            {Array.from({ length: items }).map((_, index) => (
                <div
                    key={index}
                    className="animate-pulse flex flex-col justify-between p-4 bg-gray-200 rounded-md gap-5"
                >
                        <div className="w-12 h-12 bg-gray-300 rounded"></div>
                        <div className="flex flex-col space-y-2 w-full">
                            <div className="w-24 h-3 bg-gray-300 rounded"></div>
                            <div className="w-[95%] h-2 bg-gray-300 rounded"></div>
                            <div className="w-[85%] h-2 bg-gray-300 rounded"></div>
                        </div>
                </div>
            ))}
        </div>
    );
};

export default AgentGridSkeleton;