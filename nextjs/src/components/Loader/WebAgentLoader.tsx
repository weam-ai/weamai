import React, { useState, useEffect } from 'react';

const WebAgentLoader = ({ loading }: { loading: boolean }) => {
    const [visibleIndex, setVisibleIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setVisibleIndex((prevIndex: number) => {
                if (prevIndex < 2) {
                    return prevIndex + 1;
                } else if (!loading) {
                    clearInterval(interval);
                }
                return prevIndex;
            });
        }, 2500);

        return () => clearInterval(interval);
    }, [loading]);
    return (
        <div className="my-2 animate-pulse text-font-14 font-bold inline-block">
            {visibleIndex == 0 && <p>Generating your web project proposal...</p>}
            {visibleIndex == 1 && <p>Please wait while we prepare your proposal...</p>}
            {visibleIndex == 2 && <p>This might take a few moments...</p>}
        </div> 
    )
}

export default WebAgentLoader