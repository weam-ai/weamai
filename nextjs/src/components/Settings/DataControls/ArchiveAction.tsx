'use client';

import { restoreBrainAction } from '@/actions/brains';
import { restoreWorkspaceAction } from '@/actions/workspace';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import useServerAction from '@/hooks/common/useServerActions';
import UnArchiveIcon from '@/icons/UnArchiveIcon';
import Toast from '@/utils/toast';

const UnArchiveAction = ({ data, btnname, brain = true }) => {
    const [restore, isPending] = useServerAction(restoreBrainAction);
    const [restoreWorkspace, isPendingWorkspace] = useServerAction(restoreWorkspaceAction);
    const handleRestore = async () => {
        if (brain) {
            const response = await restore(data);
            Toast(response?.message);
        } else {
            const response = await restoreWorkspace(data);
            Toast(response?.message);
        }
    }
    return (
        <TooltipProvider delayDuration={0} skipDelayDuration={0}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <button onClick={handleRestore} disabled={isPending || isPendingWorkspace}>
                        <UnArchiveIcon
                            width={18}
                            height={18}
                            className={
                                'w-[18px] h-[18px] object-contain fill-b7 hover:fill-b2'
                            }
                        />
                    </button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                    <p>{btnname}</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};

export default UnArchiveAction;

// import {
//     Tooltip,
//     TooltipContent,
//     TooltipProvider,
//     TooltipTrigger,
// } from '@/components/ui/tooltip';
// import UnArchiveIcon from '@/icons/UnArchiveIcon';

// const UnArchiveAction = ({data, restore, btnname}) => {
//     return (
//         <TooltipProvider delayDuration={0} skipDelayDuration={0}>
//             <Tooltip>
//                 <TooltipTrigger asChild>
//                     <button onClick={() => { 
//                         restore(data); 
//                     }}>
//                         <UnArchiveIcon
//                             width={16}
//                             height={16}
//                             className={
//                                 'w-[16px] h-[16px] object-contain fill-b4 hover:fill-blue'
//                             }
//                         />
//                     </button>
//                 </TooltipTrigger>
//                 <TooltipContent side="bottom">
//                     <p>{btnname}</p>
//                 </TooltipContent>
//             </Tooltip>
//         </TooltipProvider>
//     );
// };

// export default UnArchiveAction;