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
const AddBrainButton = memo(({ text, isPrivate }) => {
    const dispatch = useDispatch();
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
                    <AddBrainIcon width={18} height={(18 * 151) / 160} className="fill-b6 h-auto hover:fill-b2" />
                </button>
                </TooltipTrigger>
                <TooltipContent side="top" className="border-none">
                <p className='text-font-14'>{text}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
        
    );
});

export default AddBrainButton;
