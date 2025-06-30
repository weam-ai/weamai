import React from 'react';
const Plus = ({height, width, className}:any) => {
    return (
        <svg className={className} width={width} height={height} viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" clipRule="evenodd" d="M7.11111 16H8.88889V8.88889H16V7.11111L8.88889 7.11111V0H7.11111L7.11111 7.11111L0 7.11111V8.88889H7.11111L7.11111 16Z"/>
        </svg>
    );
};

export default Plus;
