import React from 'react';

const PlusRound = ({height, width, className}:any) => {
  return (
    <svg className={className}  width={width} height={height} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="10" cy="10" r="10" fill="white"/>
        <path d="M14.0031 9.50458H10.4031V5.90456C10.4031 5.65622 10.2015 5.45459 9.95308 5.45459C9.70475 5.45459 9.50311 5.65622 9.50311 5.90456V9.50458H5.9031C5.65476 9.50458 5.45312 9.70621 5.45312 9.95455C5.45312 10.203 5.65476 10.4046 5.9031 10.4046H9.50311V14.0045C9.50311 14.253 9.70475 14.4546 9.95308 14.4546C10.2015 14.4546 10.4031 14.253 10.4031 14.0045V10.4046H14.0031C14.2515 10.4046 14.4531 10.203 14.4531 9.95455C14.4531 9.70621 14.2515 9.50458 14.0031 9.50458Z" fill="currentColor"/>
    </svg>
  );
}

export default PlusRound;