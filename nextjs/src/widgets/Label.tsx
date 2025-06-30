const Label = ({
    title,
    htmlFor,
    Icon,
    IconWidth,
    IconHeight,
    IconClassName,
    required = true,
    className = 'text-font-14 font-semibold block mb-2 text-b2'
}:any) => {
    return (
        <label
            className={className}
            htmlFor={htmlFor}
        >
            {' '}
            {Icon && (
                <Icon
                    width={IconWidth}
                    height={IconHeight}
                    className={IconClassName}
                />
            )}{' '}
            {title}{' '}
            { required && <span className="text-red">*</span>}
        </label>
    );
};
export default Label;
