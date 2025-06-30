import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTrigger,
    DialogDescription,
    DialogTitle,
} from '@/components/ui/dialog';
import ViewIcon from '@/icons/ViewIcon';
import PromptIcon from '@/icons/Prompt';

const ViewPrompt = ({ prompt }) => {
    return (
        <Dialog>
            <DialogTrigger className='h-4'>
                <ViewIcon
                    className={
                        'fill-b5 hover:fill-b2 size-[17px] cursor-pointer transition-all ease-in-out'
                    }
                />
            </DialogTrigger>
            <DialogContent className="md:max-w-[550px] max-w-[calc(100%-30px)] py-7">
                <DialogHeader className="rounded-t-10 px-[30px] pb-3 border-b">
                    <DialogTitle className="font-semibold flex items-center">
                        <PromptIcon
                            width={24}
                            height={24}
                            className="w-6 h-auto object-contain fill-b2 me-3 inline-block align-text-top" />
                        Custom Prompts
                    </DialogTitle>
                    <DialogDescription>
                        <div className="small-description text-font-14 leading-[24px] text-b5 font-normal ml-9">
                            <p>{prompt?.title}</p>
                        </div>
                    </DialogDescription>
                </DialogHeader>
                <div className="dialog-body flex flex-col flex-1 relative h-full max-h-[650px] overflow-y-auto px-[30px] py-5">
                    <h3 className='font-bold mb-1'>Prompt Content</h3>
                    <p className='text-b6'>{prompt?.content}</p>
                    <h3 className='font-bold mb-1 mt-5'>Tags</h3>
                    <p className='text-b6'>{prompt?.tags?.join(', ')}</p>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default ViewPrompt;
