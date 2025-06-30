const OptionsVerticalIcon = ({height, width, className}:any) => {
    return (
        <svg className={className}  width={width} height={height} viewBox="0 0 4 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="2" cy="14" r="1.5" transform="rotate(-90 2 14)"/>
            <circle cx="2" cy="8" r="1.5" transform="rotate(-90 2 8)"/>
            <circle cx="2" cy="2" r="1.5" transform="rotate(-90 2 2)"/>
        </svg>
    );
};

export default OptionsVerticalIcon;
