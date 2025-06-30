

import React from 'react';

const GridIcon = ({height, width, className}:any) => {
  return (
    <svg className={className} width={width} height={height} viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path fillRule="evenodd" clipRule="evenodd" d="M6.00098 0H0.000976562V6H6.00098V0ZM4.50098 4.5H1.50098V1.5H4.50098V4.5Z"/>
        <path fillRule="evenodd" clipRule="evenodd" d="M14 0H8V6H14V0ZM12.5 4.5H9.5V1.5H12.5V4.5Z"/>
        <path fillRule="evenodd" clipRule="evenodd" d="M14 8H8V14H14V8ZM12.5 12.5H9.5V9.5H12.5V12.5Z"/>
        <path fillRule="evenodd" clipRule="evenodd" d="M6 8H0V14H6V8ZM4.5 12.5H1.5V9.5H4.5V12.5Z"/>
    </svg>

  );
}

export default GridIcon;
