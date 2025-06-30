'use client';
import { deleteSharedLinkAction } from '@/actions/settings';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import useServerAction from '@/hooks/common/useServerActions';
import RemoveIcon from '@/icons/RemoveIcon';
export const DeleteAllSharedChat = () => {
    const [deleteAction, pending] = useServerAction(deleteSharedLinkAction);
    const handleAllDelete = async () => {
        await deleteAction({ isBulk: true })
    }
    return (
        <TooltipProvider delayDuration={0} skipDelayDuration={0}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <button
                        onClick={handleAllDelete}
                        disabled={pending}
                    >
                        <RemoveIcon
                            width={18}
                            height={18}
                            className={'w-[18px] h-[18px] object-contain fill-b7 hover:fill-b2'}
                        />
                    </button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                    <p>Delete all shared links</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
};

export const DeleteSharedChat = ({share}:any) => {
    const [deleteAction, pending] = useServerAction(deleteSharedLinkAction);
    const handleDelete = async () => {
        await deleteAction({ isBulk: false, id: share._id })
    }
    return (
        <TooltipProvider
            delayDuration={0}
            skipDelayDuration={0}
        >
            <Tooltip>
                <TooltipTrigger asChild>
                    <button
                        onClick={handleDelete}
                        disabled={pending}
                    >
                        <RemoveIcon
                            width={18}
                            height={18}
                            className={'w-[18px] h-[18px] object-contain fill-b7 hover:fill-b2'}
                        />
                    </button>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                    <p>Delete Link</p>
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    )
}
