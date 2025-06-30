import BackArrowIcon from "@/icons/BackArrowIcon";

const ProAgentBack = ({ onBackHandler, code }) => {
    return (
        <div className='font-medium text-font-14 mb-3 border-b pb-3 flex items-center'>
            <button className='w-8 h-8 flex items-center justify-center rounded-md border mr-2 cursor-pointer hover:bg-b12 transition-all ease-in-out' onClick={onBackHandler}>
                <BackArrowIcon width={14} height={14} className="fill-b5 w-[12px] h-auto" />
            </button>
            {code.replace(/_/g, ' ')}
        </div>
    );
};

export default ProAgentBack;