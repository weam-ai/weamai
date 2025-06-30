const IntialScreenLoading = () => {
    return(
        <div className="loading-screen flex items-center flex-1 overflow-y-auto">
            <div className="max-w-[800px] w-full mx-auto my-[100px]">
                <div className="animate-pulse ">
                    <div className="h-[30px] max-w-[380px] mx-auto bg-gray-300 rounded mb-4 "></div>
                    <div className="flex justify-center gap-4 mt-11">
                        <div className="h-10 w-[180px] bg-gray-300 rounded"></div>
                        <div className="h-10 w-[180px] bg-gray-300 rounded"></div>
                    </div>
                    <div className="bg-white border border-b10 rounded-10 p-[30px] max-w-[672px] w-full mx-auto mt-[208px]">
                        <div className="h-6 bg-gray-300 rounded mb-4"></div>
                        <div className="h-4 bg-gray-300 rounded mb-4"></div>
                        <div className="h-4 bg-gray-300 rounded mb-4"></div>
                        <div className="h-4 bg-gray-300 rounded mb-4"></div>
                        <div className="flex justify-end mt-6">
                            <div className="h-10 w-[180px] bg-gray-300 rounded"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default IntialScreenLoading;