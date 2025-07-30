import React from 'react';
import { useState, useEffect } from 'react';

const ScrollToBottomButton = React.memo(({ contentRef }:any) => {
  const [showButton, setShowButton] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (contentRef.current) {
        const isEndOfContent =
          contentRef.current.scrollTop + contentRef.current.clientHeight + 100 >=
          contentRef.current.scrollHeight;
        setShowButton(!isEndOfContent);
      }
    };

    if (contentRef.current) {
      contentRef.current.addEventListener('scroll', handleScroll);
    }

    return () => {
      if (contentRef.current) {
        contentRef.current.removeEventListener('scroll', handleScroll);
      }
    };
  }, [contentRef]);

  const scrollToBottom = () => {
    if (contentRef.current) {
      contentRef.current.scrollTo({
        top: contentRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  };

  return (
    <>
      {showButton && <button onClick={scrollToBottom} className='w-[36px] h-[36px] bg-white border fixed bottom-8 hidden md:flex right-8 z-10 border-b10 rounded-full transition ease-in-out duration-150 items-center justify-center [&>svg]:h-[19] [&>svg]:w-[15px] [&>svg]:object-contain [&>svg]:fill-b2 hover:bg-b11'>
        <svg width="13" height="16" viewBox="0 0 15 19" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M7.22833 18.8698L0 11.6414L1.31424 10.3272L6.29917 15.3121L6.29921 0L8.15753 9.87202e-08L8.15751 15.3121L13.1424 10.3272L14.4567 11.6414L7.22833 18.8698Z"/>
        </svg>

      </button>}
    </>
  );
})

export default ScrollToBottomButton;




