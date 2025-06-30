import React from 'react';

type WarningAuditIconProps = {
    width: number;
    height: number;
    className: string;
}

const WarningAuditIcon = ({ width, height, className }: WarningAuditIconProps) => {
    return (
        <svg
            width={width}
            height={height}
            className={className}
            viewBox="0 0 84 84"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <rect width="84" height="84" />
        </svg>
    );
};

export default WarningAuditIcon;
