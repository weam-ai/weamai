import ArrowBack from '@/icons/ArrowBack';
import Link from 'next/link';

const BackButton = ({href}) => {
    return (
        <div className="back-button">
            <Link
                href={href}
                className="btn btn-dark-gray group p-0 flex items-center justify-center rounded-full w-9 h-9 min-w-9"
            >
                <ArrowBack width={"17"} height={"12"} className={"inline-block fill-b2 group-hover:fill-b15 group-focus:fill-b15 group-active:fill-b15 object-contain"}/>

            </Link>
        </div>
    );
};

export default BackButton;
