import { SvgProps } from "@/types/assets";

const DownArrowIcon = ({height, width, className, fill}:any) => {
    return (
        <svg className={className}  width={width} height={height} viewBox="0 0 15 8" fill={fill} xmlns="http://www.w3.org/2000/svg">
        <path d="M7.00525 8L14.0105 0.994746L13.0158 0L10.62 2.40981L7.00525 6.02452L3.39054 2.40981L0.994746 0.0140103L0 1.00876L7.00525 8Z" />
        </svg>
    );
};

export default DownArrowIcon;