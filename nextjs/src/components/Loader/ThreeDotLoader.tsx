import React from 'react';

const ThreeDotLoader = ({className='flex justify-center items-center h-full mt-5'}:any) => {
    return (
        <div className={className}>
            <div className="dot-flashing"></div>
        </div>
    );
};

export default ThreeDotLoader;
