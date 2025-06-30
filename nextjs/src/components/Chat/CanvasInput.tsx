import UpLongArrow from '@/icons/UpLongArrow';
import { setCanvasOptionAction } from '@/lib/slices/chat/chatSlice';
import CommonInput from '@/widgets/CommonInput';
import { useRef, useEffect, useState, forwardRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';

const CanvasInput = ({ handleSubmitPrompt, handleDeSelectionChanges, inputPosition }) => {
    const inputRef = useRef(null);
    const [question, setQuestion] = useState('');
    const dispatch = useDispatch();
    const canvasOptions = useSelector((store:any) => store.chat.canvasOptions);

    useEffect(() => {
        if (inputRef.current) {
            inputRef.current.focus();
        }
    }, []);

    const handleSubmit = () => {
        dispatch(
            setCanvasOptionAction({
                ...canvasOptions,
                question: question === '' ? 'edit or explain' : question,
            })
        );
        handleSubmitPrompt(true);
        handleDeSelectionChanges();
        setQuestion('');
    };

    return (
        <div className='pl-4 pr-[20px] pt-[6px] pb-[4px] border bg-white rounded-[25px] border-gray-300 shadow-[0_2px_7px_1px_rgba(0,0,0,0.12)]' style={{ ...inputPosition }}>
            <textarea
                className="bg-white min-w-64 overflow-y-auto outline-none focus:border-white "
                value={question}
                placeholder="edit or explain"
                onChange={(e) => setQuestion(e.target.value)}
                onInput={(e:any) => {
                    e.target.style.height = 'auto'; // Reset height
                    e.target.style.height = `${e.target.scrollHeight}px`; // Set height based on scrollHeight
                }}
                onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                        if (e.shiftKey) {
                            // Shift + Enter for new line
                            e.preventDefault();
                            setQuestion((prev) => prev + '\n');
                        } else {
                            // Regular Enter to submit
                            handleSubmit();
                        }
                    }
                }}
                onMouseUp={(e:any) => {
                    if (e.target.value) e.stopPropagation();
                    else handleDeSelectionChanges();
                }}
                onMouseDown={(e:any) => {
                    if (e.target.value) e.stopPropagation();
                    else handleDeSelectionChanges();
                }}
                autoFocus
                style={{
                    minHeight: '28px', // Default height
                    maxHeight: '110px',
                    height: '28px',
                    resize: 'none', // Prevent manual resizing
                }}
            />

            
            <button
                className="chat-submit group bg-b2 w-[30px] h-[30px] flex items-center justify-center absolute bottom-[8px] right-2 rounded-[30px] transition-colors"
                onClick={handleSubmit}
                onMouseUp={(event) => event.stopPropagation()}
                onMouseDown={(event) => event.stopPropagation()}
            >
                <UpLongArrow
                    width="13"
                    height="14"
                    className="fill-b15 group-disabled:fill-b7"
                />
            </button>
            </div>
    );
    
};


export default CanvasInput;
