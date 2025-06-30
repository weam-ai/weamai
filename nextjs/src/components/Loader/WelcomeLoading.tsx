import React from 'react';

const WelcomeLoadingUser = () => {
    return (
        <div className="h-8 bg-gray-300 rounded w-1/2 mb-2"></div>
    );
};

const FeatureLoading = () => {
    return (
        <div className="rounded-10 bg-b12 p-5 animate-pulse">
            <div className="size-[30px] bg-gray-300 rounded mb-2.5"></div>
            <div className="h-5 bg-gray-300 rounded w-3/4 mb-1.5"></div>
            <div className="h-4 bg-gray-300 rounded w-full"></div>
        </div>
    );
};

const WelcomeLoading = () => {
    return (
        <div className="flex items-start md:items-center flex-1 lg:overflow-y-auto min-h-full">
            <div className="max-w-[800px] w-full mx-auto my-6">
                <WelcomeLoadingUser />
                <div className="h-5 bg-gray-300 rounded w-full mb-5"></div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-5">
                    <FeatureLoading />
                    <FeatureLoading />
                    <FeatureLoading />
                    <FeatureLoading />
                </div>
            </div>
        </div>
    );
};

export default WelcomeLoading;