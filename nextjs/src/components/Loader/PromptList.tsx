import React from 'react';

type PromptListSkeletonProps = {
    items: number;
}

const PromptListSkeleton: React.FC<PromptListSkeletonProps> = ({ items }) => {
    return (
        <div className="space-y-4">
            {Array.from({ length: items }).map((_, index) => (
                <div
                    key={index}
                    className="animate-pulse flex flex-col justify-between p-4 bg-gray-200 rounded-md"
                >
                    <div className="flex items-center space-x-4">
                        <div className="w-40 h-4 bg-gray-300 rounded"></div>
                        <div className="w-12 h-4 bg-gray-300 rounded"></div>
                    </div>
                    <div className="w-[98%] h-4 bg-gray-300 rounded mt-3"></div>
                </div>
            ))}
        </div>
    );
};

export default PromptListSkeleton;