import React from 'react';

type PassAuditIconProps = {
    width: number;
    height: number;
    className: string;
}

const PassAuditIcon = ({ width, height, className }: PassAuditIconProps) => {
    return (
        <svg
            width={width}
            height={height}
            className={className}
            viewBox="0 0 84 84"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <circle cx="42" cy="42" r="42" />
        </svg>
    );
};

export default PassAuditIcon;
