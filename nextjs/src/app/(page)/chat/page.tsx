import { ChatItemWrapper } from '@/components/Chat/ChatWrapper';

export default function Home() {
    return (
        
        <div className="flex flex-col flex-1 relative h-full overflow-hidden">
            <div className="relative flex flex-col h-full overflow-hidden px-0 md:px-3">
                <ChatItemWrapper />
            </div>
        </div>
    );
}
