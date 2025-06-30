import React from 'react';

type PromptGridSkeletonProps = {
    items: number;
}

const PromptGridSkeleton: React.FC<PromptGridSkeletonProps> = ({ items }) => {
    return (
        
        <div className="gap-4 prompts-items-grid grid lg:grid-cols-3 grid-cols-2 lg:gap-5 max-w-[950px] mx-auto w-full col-span-3">
            {Array.from({ length: items }).map((_, index) => (
                <div
                    key={index}
                    className="animate-pulse flex flex-col justify-between p-4 bg-gray-200 rounded-md"
                >
                    <div className="flex items-center space-x-4 mb-2">
                        <div className="w-40 h-4 bg-gray-300 rounded"></div>
                    </div>
                        <div className="w-12 h-4 bg-gray-300 rounded"></div>
                    <div className="w-[98%] h-2 bg-gray-300 rounded mt-3"></div>
                    <div className="w-[90%] h-2 bg-gray-300 rounded mt-1"></div>
                </div>
            ))}
        </div>
    );
};

export default PromptGridSkeleton;