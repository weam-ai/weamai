import React from 'react';
import Select from 'react-select';

const pageSizeOptions = [
  { value: 10, label: '10' },
  { value: 20, label: '20' },
  { value: 30, label: '30' },
  { value: 100, label: '100' },
];

const DataTablePageSizeSelector = ({ pagination, handlePageSizeChange }) => {
  const selectedOption = pageSizeOptions.find(option => option.value === pagination.pageSize);

  return (
    <div className="flex items-center space-x-2">
      <span className='font-medium text-b6'>Show</span>
      <Select
        options={pageSizeOptions}
        onChange={(selectedOption) => handlePageSizeChange(selectedOption.value)}
        value={selectedOption}
        defaultValue={pageSizeOptions[0]}
        menuPosition="fixed"
        menuPlacement="auto"
        className="react-select-container react-select-border-light react-select-sm w-[100px]"
        classNamePrefix="react-select"
      />
    </div>
  );
};

export default DataTablePageSizeSelector;
