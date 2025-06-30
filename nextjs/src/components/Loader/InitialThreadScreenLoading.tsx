import React from 'react'
const InitialThreadScreenLoading = () => {
    return (
        <div className="px-2.5 py-2 w-full animate-pulse">
            <div className="flex flex-1  mx-auto gap-3 p-5 rounded-[10px]">
                <div className="flex-shrink-0 flex flex-col relative items-end">
                    <div className="h-[25px] w-[25px] -mt-1 rounded-full bg-gray-400"></div>
                </div>
                <div className="relative flex w-full flex-col">
                    <div className="flex flex-col gap-2">
                        <div className="h-4 bg-gray-300 w-1/2 rounded-custom">
                        </div>
                        <div className="h-4 bg-gray-300 w-2/3 rounded-custom">
                        </div>
                        <div className="h-4 bg-gray-300 w-3/4 rounded-custom">
                        </div>
                        <div className="h-4 bg-gray-300 w-full rounded-custom">
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
export default InitialThreadScreenLoading