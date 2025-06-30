import React from 'react';

const ExcelFileIcon = ({ width, height, className }:any) => {
    return (
        <svg
            className={className}
            width={width}
            height={height}
            viewBox="0 0 16 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <rect width="16" height="16" rx="1" fill="#0F9D58" />
            <rect x="2" y="5" width="12" height="2" fill="white" />
            <rect
                x="5"
                y="14"
                width="12"
                height="2"
                transform="rotate(-90 5 14)"
                fill="white"
            />
        </svg>
    );
};

export default ExcelFileIcon;
