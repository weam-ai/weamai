const DocsIcon = ({height, width, className}:any) => {
    return (
        <svg className={className} width={width} height={height}
            viewBox="0 0 14 16"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path 
                d="M15.1613 0H1.23523C0.553032 0 0 0.553032 0 1.23523V14.7648C0 15.447 0.553032 16 1.23523 16H15.1613C15.8435 16 16.3965 15.447 16.3965 14.7648V1.23523C16.3965 0.553032 15.8435 0 15.1613 0Z" 
                
            />
            <path 
                d="M7.40051 4L5.92271 10.9135L4.46318 4.00274L3 4.00046L4.82864 12.7636H6.65316L8.29861 5.83412L9.94407 12.7636H11.7686L13.5972 4.00046L12.134 4.00274L10.6745 10.9135L9.19672 4H7.40234H7.40051Z" 
                fill="white" 
            />
        </svg>
    );
};

export default DocsIcon;
