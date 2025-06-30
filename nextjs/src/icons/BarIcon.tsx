
import React from 'react';

const BarIcon = ({height, width, className}:any) => {
  return (
    <svg className={className}  width={width} height={height} viewBox="0 0 14 12" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="14" height="2"/>
        <rect y="5" width="14" height="2"/>
        <rect y="10" width="14" height="2"/>
    </svg>
  );
}

export default BarIcon;
    