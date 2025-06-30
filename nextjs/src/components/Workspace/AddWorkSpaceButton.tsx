import AddIcon from '@/icons/AddIcon';

const AddWorkspaceButton = ({ click }) => {
    return (
        <span
            onClick={click}
            className="flex items-center whitespace-nowrap text-b2 text-font-18 leading-[22px] font-bold cursor-pointer focus:outline-none has-[:checked]:bg-b12 hover:bg-b12"
        >
            <span className="add-icon rounded-full flex items-center justify-center size-[30px] bg-b10 mr-2.5">
                <AddIcon
                    width={'12'}
                    height={'12'}
                    className="size-3 fill-b5"
                />
            </span>
            <span className="flex-1">Add a Workspace</span>
        </span>
    );
};

export default AddWorkspaceButton;
