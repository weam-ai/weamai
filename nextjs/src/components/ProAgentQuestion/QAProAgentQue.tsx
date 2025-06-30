import Customgpt from "@/icons/Customgpt";
// import { GlobeIcon } from "lucide-react";
import GlobeIcon from "@/icons/GlobalIcon";

const QAProAgentQuestion = ({code, url}) => {
    return (
        <>
            <p className='text-font-14 font-bold flex items-center gap-x-1'>
                <Customgpt
                    width={'16'}
                    height={'16'}
                    className="mr-2 fill-b5"
                />
                Agent: {code.replace(/_/g, ' ')}
            </p>
            <div className='text-font-14 flex items-center gap-x-1'>
                <GlobeIcon
                    width={'16'}
                    height={'16'}
                    className="mr-2 fill-b5"
                />
                URL: {url}
            </div>
        </>
    );
}

export default QAProAgentQuestion;