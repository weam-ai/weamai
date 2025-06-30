import ArrowBack from '@/icons/ArrowBack';

type CVScreeningProps = {
    onBackHandler: () => void;
}

const CVScreening = ({ onBackHandler }: CVScreeningProps) => {
    return (
        <div className="qa-form">
            <div className="relative mb-4">
                <label
                    htmlFor="url"
                    className="text-font-14 font-semibold text-b2 cursor-pointer mb-2 inline-block"
                >
                    Website URL
                </label>
                <input
                    type="text"
                    placeholder="Enter the website URL to analyze (e.g., https://www.example.com)"
                    className="default-form-input"
                    id="url"
                    maxLength={50}
                />
            </div>
            <div className="relative mb-4 flex gap-2">
                <button className="btn btn-outline-black text-font-14 flex [&>svg]:hover:fill-white" onClick={onBackHandler}>
                    <ArrowBack width={16} height={16} className="fill-b2 w-[16px] h-auto mr-1" /> Back
                </button>
                <button className="btn btn-outline-black text-font-14">
                    Run Agent
                </button>
            </div>
        </div>
    );
};

export default CVScreening;
