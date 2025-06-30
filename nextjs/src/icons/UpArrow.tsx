import React from 'react';

const UpArrow = ({height, width, className}:any) => {
  return (
    <svg className={className} width={width} height={height} viewBox="0 0 10 5" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M4.51221 0L9.01221 4.37828L8.37321 5L6.83421 3.49387L4.51221 1.23468L2.19021 3.49387L0.651207 4.99124L0.012207 4.36953L4.51221 0Z"/>
    </svg>

  );
}

export default UpArrow;
