
export const customSelectStyles = {
    menu: (provided) => ({
        ...provided,
        zIndex: 1000, // Ensure the dropdown menu is above other content
        position: 'absolute',
    }),
    menuList: (provided) => ({
        ...provided,
        maxHeight: '150px', // Adjust as needed to prevent overflow
        overflowY: 'auto',
    }),
    option: (provided, state) => ({
        ...provided,
        cursor: state.isDisabled ? 'not-allowed' : 'pointer',
        color: state.isDisabled ? '#B6B6B6' : '#121212',
        // backgroundColor: state.isDisabled ? '#B6B6B6' : '#121212',
    }),
};

