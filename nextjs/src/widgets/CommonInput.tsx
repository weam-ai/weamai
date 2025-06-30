import React, { InputHTMLAttributes, ForwardedRef } from 'react';

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
    className?: string;
    placeholder?: string;
    onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onClick?: (e: React.MouseEvent<HTMLInputElement>) => void;
    defaultValue?: string;
    value?: string;
    checked?: boolean;
};

const CommonInput: React.FC<InputProps> = React.forwardRef(({
    type = 'text',
    className = 'default-form-input',
    placeholder,
    onChange,
    onClick,
    defaultValue,
    value,
    checked,
    id,
    name,
    ...rest
}, ref: ForwardedRef<HTMLInputElement>) => {
    return (
        <input
            type={type}
            className={className}
            placeholder={placeholder}
            onChange={onChange}
            onClick={onClick}
            defaultValue={defaultValue}
            value={value}
            checked={type === "checkbox" ? checked : undefined}
            id={id}
            name={name}
            ref={ref}
            {...(type === 'email' && { style: { textTransform: 'lowercase' } })}
            {...rest}
        />
    );
});

export default CommonInput;
