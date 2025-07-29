import useChatMember from '@/hooks/chat/useChatMember';
import BookMarkIcon, { ActiveBookMark } from '@/icons/Bookmark';
import { useParams } from 'next/navigation';
import { useSelector } from 'react-redux';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';

const Bookmark = () => {
    const favourite = useSelector((store:any) => store.chat.favourite);
    const { favouriteChat } = useChatMember();
    const params = useParams();
    const handleBookmark = () => {
        favouriteChat(!favourite, params.id);
    };
    return (
        <TooltipProvider>
        <Tooltip>
            <TooltipTrigger asChild>
            <button className={`bookmarkedbutton w-9 lg:w-10 lg:min-w-10 h-9 lg:h-10 rounded-full p-1 lg:p-2 flex items-center justify-center border border-b11 hover:bg-b11 [&>svg]:fill-b2 [&>svg]:fill-h-4 [&>svg]:w-4 [&>svg]:object-contain overflow-hidden ${
                favourite ? 'active' : ''
            }`}
            onClick={handleBookmark}>
                {favourite ? <ActiveBookMark /> : <BookMarkIcon />}
            </button>
            </TooltipTrigger>
            <TooltipContent>
            <p className='text-font-14'>Add to Favorites</p>
            </TooltipContent>
        </Tooltip>
        </TooltipProvider>
    );
};

export default Bookmark;
