const Humburger = ({ height, width, className }) => {
    return (
        <svg
            className={className}
            width={width}
            height={height}
            viewBox="0 0 246 119"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M0 15C0 6.71573 6.71573 0 15 0H231C239.284 0 246 6.71573 246 15C246 23.2843 239.284 30 231 30H15C6.71573 30 0 23.2843 0 15Z"
            />
            <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M0 104C0 95.7157 6.71573 89 15 89H162C170.284 89 177 95.7157 177 104C177 112.284 170.284 119 162 119H15C6.71573 119 0 112.284 0 104Z"
            />
        </svg>
    );
};

export default Humburger;
