import React, { useState, useEffect } from 'react';

const SalesCallLoader = ({ loading }: { loading: boolean }) => {
    const [visibleIndex, setVisibleIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setVisibleIndex((prevIndex: number) => {
                if (prevIndex < 5) {
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
            {visibleIndex == 0 && <p>Analyzing your sales call for upselling opportunities...</p>}
            {visibleIndex == 1 && <p>Identifying call highlights...</p>}
            {visibleIndex == 2 && <p>Analyzing client needs...</p>}
            {visibleIndex == 3 && <p>Searching for upselling and cross-selling opportunities...</p>}
            {visibleIndex == 4 && <p>Generating a your call report...</p>}
            {visibleIndex == 5 && <p>Almost done — finalizing insights...</p>}
        </div> 
    )
}

export default SalesCallLoader