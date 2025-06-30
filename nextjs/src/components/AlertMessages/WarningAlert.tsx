import React from 'react';

const WarningAlert = ({ description, className }) => {
  return (
    <div className={`bg-orange/10 text-orange text-font-16 font-normal px-4 py-2.5 rounded-custom ${className}`}>
      {description}
    </div>
  );
};

export default WarningAlert;