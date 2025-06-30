import React from 'react';
import { SvgProps } from '@/types/assets';

const PurpleTick = ({ height, width, className, fill }: SvgProps) => {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width={width}
            height={height}
            viewBox="0 0 14 12"
            fill="none"
            className={className}
        >
            <path
                d="M13.7 1.20039C13.3 0.800391 12.7 0.800391 12.3 1.20039L4.8 8.70039L1.7 5.60039C1.3 5.20039 0.7 5.20039 0.3 5.60039C-0.1 6.00039 -0.1 6.60039 0.3 7.00039L4.1 10.8004C4.3 11.0004 4.5 11.1004 4.8 11.1004C5.1 11.1004 5.3 11.0004 5.5 10.8004L13.7 2.60039C14.1 2.20039 14.1 1.60039 13.7 1.20039Z"
                fill={fill}
            />
        </svg>
    );
};

export default PurpleTick;
