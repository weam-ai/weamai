import Customgpt from "@/icons/Customgpt";
import GlobeIcon from "@/icons/GlobalIcon";
import PromptIcon from "@/icons/Prompt";

const VideoCallAgent = ({proAgentData}) => {
    return (
        <>
            <p className='text-font-14 font-bold flex items-center gap-x-1'>
                <Customgpt
                    width={'16'}
                    height={'16'}
                    className="mr-2 fill-b5"
                />
                Agent: {proAgentData?.code.replace(/_/g, ' ')}
            </p>
            <div className='text-font-14 flex mt-2 gap-x-1'>
                <GlobeIcon
                    width={'16'}
                    height={'16'}
                    className="mr-2 fill-b5 min-w-4 mt-1"
                /> 
                {proAgentData?.url}
            </div>
            <div className='text-font-14 flex items-center gap-x-1 mt-3 flex-wrap border-t pt-2'>
                <PromptIcon
                width={'16'}
                height={'16'}
                className="mr-2 fill-b5 min-w-4" />
                <span className="text-b2 font-medium">Prompt:</span> <span className="w-full">{proAgentData?.prompt}</span>
            </div>
        </>
    );
}

export default VideoCallAgent;