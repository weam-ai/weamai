import React, { useState, useEffect } from 'react';

const VideoCallAgentLoader = ({ loading }: { loading: boolean }) => {
    const [visibleIndex, setVisibleIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setVisibleIndex((prevIndex: number) => {
                if (prevIndex < 4) {
                    return prevIndex + 1;
                } else if (!loading) {
                    clearInterval(interval);
                }
                return prevIndex;
            });
        }, 10000);

        return () => clearInterval(interval);
    }, [loading]);
    return (
        <div className="my-2 animate-pulse text-font-14 font-bold inline-block">
            {visibleIndex == 0 && <p>Analyzing video content...</p>}
            {visibleIndex == 1 && <p>Extracting key moments and insights...</p>}
            {visibleIndex == 2 && <p>Scanning for important highlights...</p>}
            {visibleIndex == 3 && <p>This won’t take long...</p>}
            {visibleIndex == 4 && <p>Almost there—getting the details ready...</p>}
        </div> 
    )
}

export default VideoCallAgentLoader