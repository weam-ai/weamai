import Plus from "@/icons/Plus";

const PlusButton = ({ text, className, onClick }) => {
    return (
        <button className={`cursor-pointer flex items-center px-1 my-5 rounded-custom [&.active]:bg-b11 ${className}`} onClick={onClick}>
            <span className="mr-2.5 w-5 h-5 min-w-5 bg-b10 rounded-full flex items-center justify-center">
                <Plus width={10} height={10} className="h-2.5 w-2.5 object-contain fill-b5"/>
            </span>
            <span className="text-font-14 leading-[19px] text-b6 font-semibold">
                {text}
            </span>
        </button>
    );
};

export default PlusButton;
