import DownArrowIcon from '@/icons/DownArrow';
import UpArrow from '@/icons/UpArrow';
import React, { useState } from 'react';

const StorageSelector = ({ min = 0, max = 1000, step = 1, initialValue = 100, unit = 'mb', onChange, className = '' }:any) => {
  const [currentValue, setCurrentValue] = useState(initialValue);

  const handleIncrement = (e) => {
    e.preventDefault();
    const newValue = Math.min(currentValue + step, max);
    setCurrentValue(newValue);
    if (onChange) onChange(newValue);
  };

  const handleDecrement = (e) => {
    e.preventDefault();
    const newValue = Math.max(currentValue - step, min);
    setCurrentValue(newValue);
    if (onChange) onChange(newValue);
  };

  const handleChange = (e) => {
    const numericValue = parseInt(e.target.value.replace(unit, '')) || 0;
    const newValue = Math.max(Math.min(numericValue, max), min);
    setCurrentValue(newValue);
    if (onChange) onChange(newValue);
  };

  return (
    <div className={`number-input inline-flex border border-b10 rounded-custom overflow-hidden ${className}`}>
      <div 
        className='h-10 text-font-14 font-normal text-b2 border-0 w-[65px] p-2.5 flex items-center'
      >
        {`${currentValue}${unit}`}
      </div>
      <div className='border-l border-b10 flex flex-col'>
        <button type="button" onClick={handleIncrement} disabled={currentValue >= max} className='flex items-center justify-center transition ease-in-out w-[30px] focus:outline-none bg-none flex-1 hover:bg-b12'>
          <UpArrow className="w-2.5 h-[5px] fill-b5" />
        </button>
        <button type="button" onClick={handleDecrement} disabled={currentValue <= min} className="flex items-center justify-center transition ease-in-out w-[30px] focus:outline-none bg-none flex-1 hover:bg-b12 border-t border-b10">
          <DownArrowIcon className="w-2.5 h-[5px] fill-b5" />
        </button>
      </div>
    </div>
  );
};

export default StorageSelector;