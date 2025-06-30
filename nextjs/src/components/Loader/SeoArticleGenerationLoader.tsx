import React, { useState, useEffect } from 'react';

const SeoArticleGenerationLoader = ({ loading }) => {
    const [visibleIndex, setVisibleIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setVisibleIndex((prevIndex) => {
                if (prevIndex < 4) {
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
            {visibleIndex == 0 && <p>Starting the article generation process...</p>}
            {visibleIndex == 1 && <p>Generating the article structure...</p>}
            {visibleIndex == 2 && <p>Optimizing the article...</p>}
            {visibleIndex == 3 && <p>Writing engaging content...</p>}
            {visibleIndex == 4 && <p>Polishing the article...</p>}
        </div>           
    );
};

const SeoKeywordLoader = () => {
    return <>
        <div className="my-2 animate-pulse text-font-14 font-bold inline-block">
            Analyzing SEO keywords...
        </div>
    </>
}

const SeoTopicLoader = () => {
    return <>
        <div className="my-2 animate-pulse text-font-14 font-bold inline-block">
            Generating topic based on your targeted keywords...
        </div>
    </>
}

export { SeoArticleGenerationLoader, SeoKeywordLoader, SeoTopicLoader };