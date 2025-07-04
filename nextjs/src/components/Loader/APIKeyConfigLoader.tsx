import React from 'react';

type APIKeyConfigLoaderProps = {
    count?: number;
}

const APIKeyConfigLoader = ({ count = 3 }: APIKeyConfigLoaderProps) => {
    return (
        <div className="flex flex-col gap-4 mt-5">
            {[...Array(count)].map((_, idx) => (
                <div
                    key={idx}
                    className="border-b last:border-none px-2 py-3 flex items-center gap-2 animate-pulse"
                >
                    <div className="w-6 h-6 rounded-full bg-gray-300" />
                    <div className="h-4 bg-gray-300 rounded w-32" />
                    <div className="h-4 bg-gray-300 rounded w-20 ml-auto" />
                </div>
            ))}
        </div>
    )
}

export default APIKeyConfigLoader