import React from 'react';

const RightArrow = ({height, width, className}:any) => {
  return (
    <svg className={className}  width={width} height={height} viewBox="0 0 6 11" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M6 5.74606L0.746059 0.492119L-4.26703e-07 1.23818L1.80735 3.03503L4.51839 5.74606L1.80736 8.45709L0.0105077 10.2539L0.756567 11L6 5.74606Z"/>
    </svg>
  );
}

export default RightArrow;
