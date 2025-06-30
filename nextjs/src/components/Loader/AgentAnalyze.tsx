import React, { useState, useEffect } from 'react';

const AgentAnalyze = ({ loading }) => {
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
        }, 3500);

        return () => clearInterval(interval);
    }, [loading]);

    return (
        <div className="my-2 animate-pulse text-font-14 font-bold inline-block">
            {visibleIndex == 0 && <p>Fetching data from the website...</p>}
            {visibleIndex == 1 && <p>Analyzing website content and structure...</p>}
            {visibleIndex == 2 && <p>Generating the QA analysis report...</p>}
        </div>           
    );
};

export default AgentAnalyze;