import React from 'react';

const AscendingIcon = ({ height, width, className }: any) => {
    return (
        <svg
            className={className}
            width={width}
            height={height}
            viewBox="0 0 335 664"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                d="M161.894 3C164.203 -1 169.976 -0.999995 172.286 3.00001L333.367 282C335.676 286 332.789 291 328.17 291H6.00894C1.39014 291 -1.4966 286 0.8128 282L161.894 3Z"
                fill="#656565"
            />
            <path
                d="M161.894 661C164.203 665 169.976 665 172.286 661L333.367 382C335.676 378 332.789 373 328.17 373H6.00894C1.39014 373 -1.4966 378 0.8128 382L161.894 661Z"
                fill="#989898"
            />
        </svg>
    );
};

export default AscendingIcon;
