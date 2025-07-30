'use client';
import React from 'react';
import SearchIcon from '@/icons/Search';

const DataTableSearch = ({
    placeholder,
    handleFilterChange,
    value,
    width='max-w-[400px]',
    ...rest
}) => {
    return (
        <div className={`search-wrap relative ${width} flex-1 md:mb-0 mb-2`}>
            <input
                {...rest}
                value={value}
                onChange={handleFilterChange}
                placeholder={placeholder}
                className="default-form-input default-form-input-md !border-b10 focus:!border-b2 !pl-10"
            />
            <span className="inline-block absolute left-[15px] top-1/2 -translate-y-1/2 [&>svg]:fill-b7">
                <SearchIcon className="w-4 h-[17px] fill-b7" />
            </span>
        </div>
    );
};

export default DataTableSearch;
