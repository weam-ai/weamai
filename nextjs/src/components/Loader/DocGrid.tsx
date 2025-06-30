import React from 'react';

type DocGridSkeletonProps = {
    items: number;
}

const DocGridSkeleton: React.FC<DocGridSkeletonProps> = ({ items }) => {
    return (
        <div className="gap-4 prompts-items-grid grid lg:grid-cols-3 grid-cols-2 lg:gap-5 max-w-[950px] mx-auto w-full col-span-3">
            {Array.from({ length: items }).map((_, index) => (
                <div
                    key={index}
                    className="animate-pulse flex flex-col justify-between p-4 bg-gray-200 rounded-md flex-wrap md:flex-nowrap"
                >
                    <div className="flex flex-col w-full md:w-[45%] md:mb-0 mb-2">
                        <div className="w-12 h-12 bg-gray-300 rounded mb-1"></div>
                    </div>
                    <div className="flex items-center w-full gap-2">
                        <div className="w-5 h-5 bg-gray-300 rounded mb-1"></div>
                        <div className="w-40 h-3 bg-gray-300 rounded"></div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <div className="w-6 h-6 bg-gray-300 rounded-full"></div>
                        <div>
                            <div className="w-20 h-2 bg-gray-300 rounded"></div>
                            <div className="w-16 h-2 bg-gray-300 rounded mt-1"></div>
                        </div>
                        
                    </div>
                    <div className="flex items-center space-x-2">
                    </div>
                </div>
            ))}
        </div>
    );
};

export default DocGridSkeleton;