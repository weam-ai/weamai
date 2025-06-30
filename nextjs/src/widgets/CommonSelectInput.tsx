import React from 'react';
import Select from 'react-select';

const CommonSelectInput = React.forwardRef(
    ({ className = 'react-select-container', options, side, ...rest }, ref) => {
        return (
            <Select
                options={options}
                className={className}
                menuPlacement={side}
                classNamePrefix="react-select"
                {...rest}
                ref={ref}
            />
        );
    }
);

export default CommonSelectInput;
