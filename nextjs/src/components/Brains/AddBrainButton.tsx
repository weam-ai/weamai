'use client';
import { memo } from 'react';
import AddBrainIcon from '@/icons/AddBrainIcon';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
import { useDispatch } from 'react-redux';
import { setModalStatus, setToPrivateBrain } from '@/lib/slices/brain/brainlist';
import { useSidebar } from '@/context/SidebarContext';
const AddBrainButton = memo(({ text, isPrivate }) => {
    const dispatch = useDispatch();
    const { isCollapsed } = useSidebar();
    
    // Determine tooltip side based on sidebar collapse state
    const tooltipSide = isCollapsed ? "right" : "top";
    
    const handleBrainButtonClick = () => {
        if (isPrivate) dispatch(setToPrivateBrain(true));
        else dispatch(setToPrivateBrain(false));
        dispatch(setModalStatus(true));
    };
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                <button
                    className="cursor-pointer"
                    onClick={handleBrainButtonClick}
                >   
                    <span className='collapsed-brain'>
                        <AddBrainIcon width={18} height={(18 * 151) / 160} className="fill-b6 collapsed-icon h-auto hover:fill-b2" />
                    </span>
                    <span className='font-medium whitespace-nowrap text-font-12 px-2 py-1 rounded-[12px] bg-blue3 text-blue2 collapsed-text'>+ Add</span>
                </button>
                </TooltipTrigger>
                <TooltipContent side={tooltipSide} className="border-none">
                <p className='text-font-14 font-normal'>{text}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
        
    );
});

export default AddBrainButton;
