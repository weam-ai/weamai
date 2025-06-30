import React from 'react';

const DefaultButton = ({ className, text, rest }) => {
    return (
        <button className={className} {...rest}>
            {text}
        </button>
    );
};

export default DefaultButton;
