import React, {forwardRef } from 'react';
import Select from 'react-select';
import Label from '@/widgets/Label';
import ValidationError from '@/widgets/ValidationError';

const ChipsInput = (props,ref) => {

    const { optionBindObj, options, label, showLabel = true, value, inputValue, setValue, handleSearch, setFormValue, name, required, errors,clearErrors, ...rest }=props
    const customSelectStyles = {
        valueContainer: (provided) => ({
            ...provided,
            maxHeight: '90px',  
        }),
        menu: (provided) => ({
            ...provided,
            zIndex: 9999,
        }),
        menuList: (provided) => ({
            ...provided,
            zIndex: 9999,
            overflowY: 'auto',
        }),
        dropdownIndicator: (base) => ({
            display: 'none'
        }),
        multiValueRemove: (base, state) => {
            return state.data.isFixed ? { ...base, display: 'none' } : base;
        },
        multiValue: (base, state) => {
            return state.data.isFixed
                ? { ...base, backgroundColor: 'gray' }
                : base;
        },
        multiValueLabel: (base, state) => {
            return state.data.isFixed
                ? {
                      ...base,
                      fontWeight: 'bold',
                      color: 'white',
                      paddingRight: 6,
                  }
                : base;
        },
    };

    const handleInputChange = (inputValue) => {
        handleSearch(inputValue); 
    };

    const handleChange = (newValue, actionMeta) => {
        switch (actionMeta.action) {
            case 'remove-value':
            case 'pop-value':
                if (actionMeta.removedValue?.isFixed) {
                    return;
                }
                break;
            case 'clear':
                actionMeta.removedValues?.forEach((currRemovedValue) => {
                    if (currRemovedValue.isFixed) {
                        newValue = [...newValue, currRemovedValue]; 
                    }
                });
                break;
        }
    
        setFormValue(name, newValue, { shouldDirty: true });
    
        if (newValue.length > 0) {
            clearErrors?.(name);
        }
    };

    return (
        <div className="w-full">
            {showLabel && <Label title={label} required={required} />}

            <Select
                {...rest}
                ref={ref}
                options={options?.map((op) => {
                    return {
                        ...op,
                        value: op[optionBindObj.value],
                        label: op[optionBindObj.label],
                    };
                })}
                styles={customSelectStyles}
                menuPlacement="auto"
                isMulti
                className="react-select-container"
                classNamePrefix="react-select"
                onInputChange={handleInputChange}
                inputValue={inputValue}
                isClearable={value?.some((v) => !v.isFixed)}
                onChange={handleChange}
                value={value}
            />
            <ValidationError errors={errors} field={name}></ValidationError>
        </div>
    );
};

export default forwardRef(ChipsInput);
