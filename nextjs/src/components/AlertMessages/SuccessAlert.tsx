import React from 'react';

const SuccessAlert = ({ description, className }) => {
  return (
    <div className={`bg-green/10 text-greendark text-font-16 font-normal px-4 py-2.5 rounded-custom ${className}`}>
      {description}
    </div>
  );
};

export default SuccessAlert;