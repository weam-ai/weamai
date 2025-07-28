import React, { useState, useCallback } from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import ForkIcon from '@/icons/ForkIcon';
import EditIcon from '@/icons/Edit';
import CheckIcon from '@/icons/CheckIcon';
import { useSelector } from 'react-redux';
import useForkChat from '@/hooks/chat/useForkChat';
import { MarkOutPut } from '@/components/Chat/MartOutput';
import LockIcon from '@/icons/Lock';
import { ShareBrainIcon } from '@/icons/Share';
import Label from '@/widgets/Label';
import CommonSelectInput from '@/widgets/CommonSelectInput';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { forkChatSchema, ForkChatSchemaType } from '@/schema/chat';
import ValidationError from '@/widgets/ValidationError';
import { displayName, getModelImageByCode } from '@/utils/common';
import ProfileImage from '../Profile/ProfileImage';
import { RootState } from '@/lib/store';
import { ConversationType } from '@/types/chat';
import { DynamicImage } from '@/widgets/DynamicImage';
import { LINK } from '@/config/config';
import RenderAIModalImage from './RenderAIModalImage';
import ProAgentQuestion from './ProAgentQuestion';
import { API_TYPE_OPTIONS, getModelImageByName } from '@/utils/constant';
import PageSpeedResponse from './PageSpeedResponse';
import { PAGE_SPEED_RECORD_KEY } from '@/hooks/conversation/useConversation';
import { getDisplayModelName } from '@/utils/helper';
import ChatUploadedFiles from './ChatUploadedFiles';

type BrainButtonsProps = {
    text: string,
    share?: boolean,
    selectedOption: string,
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void,
    className?: string
}

const defaultValues:any = {
    type: undefined
}

const generateBrainOptions = (combinedBrain, filter) => 
    combinedBrain.reduce((acc, curr) => {
        if (curr.isShare === filter) {
            acc.push({
                value: curr.title,
                label: curr.title,
                slug: curr.slug,
                user: curr.user,
                id: curr._id
            });
        }
        return acc;
    }, []);

const BrainButtons = ({ text, share, selectedOption, onChange }: BrainButtonsProps) => {
    return (
        <div className="relative">
            <label
                className="group cursor-pointer btn btn-gray md:py-[11px] my-2 lg:px-8 px-3 hover:bg-green mx-2 hover:border-green active:bg-green active:border-green checked:bg-green checked:border-green has-[:checked]:text-b15 has-[:checked]:bg-green has-[:checked]:border-green text-font-14"
                htmlFor={text}
            >
                <input
                    className="group-button peer"
                    type="radio"
                    name="flexRadioDefault"
                    id={text}
                    value={text}
                    checked={selectedOption === text}
                    onChange={onChange}
                />
                <span className='max-md:hidden'>
                {share ? (
                    <ShareBrainIcon
                        className="fill-b6 peer-checked:fill-b15 group-hover:fill-b15 group-active:fill-b15 transition duration-150 ease-in-out inline-block mr-2.5 w-auto h-[18px] object-contain"
                        width={'20'}
                        height={'18'}
                    />
                ) : (
                    <LockIcon
                        className="fill-b6 peer-checked:fill-b15 group-hover:fill-b15 group-active:fill-b15 transition duration-150 ease-in-out inline-block mr-2.5 w-auto h-[18px] object-contain"
                        width={'14'}
                        height={'18'}
                    />
                )}
                </span>

                {text}
            </label>
        </div>
    );
};

const ForkChatModal = ({ open, closeModal, forkData }) => {
    const [isEditing, setIsEditing] = useState(false);
    const chatTitle = useSelector((store: RootState) => store.conversation.chatTitle);
    const combinedBrain = useSelector((store: RootState) => store.brain.combined); 
    const [title, setTitle] = useState(`Fork Of ${chatTitle}`);
    const [editedTitle, setEditedTitle] = useState(title);
    const [forkStatus, setForkStatus] = useState('Private Fork');
    const [brainOptions, setBrainOptions] = useState(generateBrainOptions(combinedBrain, false));
    const [selectedBrain, setSelectedBrain] = useState(null);
    const { loading, createNewForkChat } = useForkChat();

    const { register, handleSubmit, formState: { errors }, setValue } = useForm<ForkChatSchemaType>({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        defaultValues,
        resolver: yupResolver(forkChatSchema)
    })

    const handleEditClick = () => {
        setIsEditing(true);
        setEditedTitle(title); // Reset editedTitle to the current title
    };

    const handleSaveClick = () => {
        setIsEditing(false);
        setTitle(editedTitle); // Save the edited title
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setEditedTitle(e.target.value);
    };

    const handlePrivateClick = useCallback(() => {
        setForkStatus('Private Fork');
        setBrainOptions(generateBrainOptions(combinedBrain, false));
    }, [forkStatus])

    const handleShareClick = useCallback(() => {
        setForkStatus('Shared Fork');
        setBrainOptions(generateBrainOptions(combinedBrain, true));
    }, [forkStatus])

    return (
        <Dialog open={open} onOpenChange={closeModal}>
            <DialogContent className="md:max-w-[730px] max-w-[calc(100%-30px)] overflow-y-auto max-h-[calc(100vh-100px)]">
                <DialogHeader className="rounded-t-10 px-[30px] pt-6">
                    <DialogTitle className="text-font-18 font-bold text-b2">
                        <ForkIcon className="w-auto h-6 min-w-6 object-contain fill-b2 me-4 inline-block align-text-top" />
                        Fork Chat
                    </DialogTitle>
                    <DialogDescription>
                    <div className="small-description text-font-15 leading-[24px] text-b5 font-normal md:mt-5 mt-3">
                        <p>
                            Forking this conversation will generate a fresh
                            Shared chat that encompasses all prior messages
                            alongside this one.
                        </p>
                    </div>    
                    </DialogDescription>
                    
                    <div className="modal-body-title flex items-center justify-between border-x border-t border-b11 bg-b11 md:px-[30px] px-3 md:py-[13px] py-2 rounded-t-10 mt-6">
                        {isEditing ? (
                            <input
                                type="text"
                                className="flex-1 mr-3 p-0 m-0 border-1 border-transparent outline-none bg-transparent text-font-18 leading-[28px] font-semibold text-b2 focus:border-b6"
                                value={editedTitle}
                                onChange={handleInputChange}
                                autoFocus
                            />
                        ) : (
                            <h5 className="body-title text-font-16 leading-[28px] font-semibold text-b2 my-0 mr-3">
                                {title}
                            </h5>
                        )}
                        {isEditing ? (
                            <button
                                type="button"
                                className="edit-title w-10 min-w-10 h-10 flex items-center justify-center rounded-full hover:bg-b10 outline-none"
                                onClick={handleSaveClick}
                            >
                                <CheckIcon className="h-5 w-5 object-contain fill-b6" />
                            </button>
                        ) : (
                            <button
                                type="button"
                                className="edit-title w-10 min-w-10 h-10 flex items-center justify-center rounded-full hover:bg-b10 outline-none"
                                onClick={handleEditClick}
                            >
                                <EditIcon className="h-5 w-5 object-contain fill-b6" />
                            </button>
                        )}
                    </div>
                </DialogHeader>
                <div className="dialog-body flex flex-col flex-1 relative h-full overflow-hidden px-[30px]">
                    {/*Modal Body start */}
                    <div className="h-full border-x border-b border-b11 rounded-b-10 pr-2.5 pt-5 pb-2">
                        <div className="h-full w-full">
                            {/* Chat Start*/}
                            {/* Shared Chat start*/}
                            <div className="shared-chat-block chat-wrap flex flex-col flex-1">
                                {/* Chat item Start*/}
                                {forkData.length > 0 &&
                                    forkData.map((fork: ConversationType, i: number) => {
                                        return (
                                            <React.Fragment key={i}>
                                                <div className="chat-item w-full md:pl-[30px] md:pr-2.5 px-2.5 mb-5 last:mb-0">
                                                    <div className="justify-center text-font-16 text-b2 m-auto">
                                                        <div className="relative group flex flex-1 text-font-16 mx-auto gap-3">
                                                            <div className="flex-shrink-0 flex flex-col relative items-end">
                                                                <div className="pt-0.5">
                                                                    <div className="relative flex w-6 h-6 items-center justify-center overflow-hidden rounded-full">
                                                                        <ProfileImage
                                                                            user={
                                                                                fork?.user
                                                                            }
                                                                            w={
                                                                                25
                                                                            }
                                                                            h={
                                                                                25
                                                                            }
                                                                            classname={
                                                                                'user-img w-[25px] h-[25px] rounded-full object-cover'
                                                                            }
                                                                            spanclass={
                                                                                'user-char flex items-center justify-center size-6 rounded-full bg-[#B3261E] text-b15 text-font-12 font-normal'
                                                                            }
                                                                        />
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div className="relative flex w-full flex-col">
                                                                <div className="font-bold select-none mb-1">
                                                                    {displayName(fork.user)}
                                                                </div>
                                                                <div className="flex-col gap-1 md:gap-3">
                                                                    <div className="flex flex-grow flex-col max-w-full">
                                                                        <div className="min-h-[20px] text-message flex flex-col items-start gap-3 whitespace-pre-wrap break-words [.text-message+&]:mt-5 overflow-x-auto">
                                                                            <ChatUploadedFiles
                                                                                media={fork?.cloneMedia}
                                                                                customGptId={fork?.customGptId}
                                                                                customGptTitle={fork?.customGptTitle}
                                                                                gptCoverImage={fork?.coverImage}
                                                                            />
                                                                            <div className="">
                                                                                { fork?.responseAPI == API_TYPE_OPTIONS.PRO_AGENT &&
                                                                                    <ProAgentQuestion proAgentData={fork?.proAgentData} />
                                                                                }
                                                                                { fork?.responseAPI != API_TYPE_OPTIONS.PRO_AGENT &&
                                                                                    fork.message
                                                                                }
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                                {/* Chat item End*/}
                                                {/* Chat item Start*/}
                                                <div className="chat-item w-full md:pl-[30px] md:pr-2.5 px-2.5 last:mb-0">
                                                    <div className="justify-center text-font-16 text-b2 m-auto">
                                                        <div className="relative group flex flex-1 text-font-16 mx-auto gap-3">
                                                            <div className="flex-shrink-0 flex flex-col relative items-end">
                                                                <RenderAIModalImage
                                                                    src={getModelImageByName(fork.responseModel)}
                                                                    alt={fork.responseModel}
                                                                />
                                                            </div>
                                                            <div className="relative w-full">
                                                                <div className="font-bold select-none mb-1">
                                                                    {
                                                                        getDisplayModelName(fork.responseModel)
                                                                    }
                                                                </div>
                                                                <div className="break-words min-h-[20px]">
                                                                    <div className="chat-content max-w-none w-full break-words text-font-16 leading-[28px] tracking-[0.16px]">
                                                                        {
                                                                            fork.response.startsWith('images/') ? 
                                                                                <DynamicImage src={`${LINK.AWS_S3_URL}/${fork.response}`} alt={fork.response} width={200} height={200} placeholder='blur'/>
                                                                            :
                                                                            <>
                                                                                {MarkOutPut(fork.response)}
                                                                                {
                                                                                    fork?.responseAddKeywords?.hasOwnProperty(PAGE_SPEED_RECORD_KEY) && <PageSpeedResponse response={fork?.responseAddKeywords} />
                                                                                }
                                                                            </>
                                                                        }
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </React.Fragment>
                                        );
                                    })}
                                {/* Chat item End*/}
                            </div>
                            {/* Shared Chat End */}
                            {/* chat End */}
                        </div>
                    </div>
                    {/*Modal Body End */}
                    {/*Modal Footer Start */}
                    
                    <div className="flex items-center flex-wrap lg:flex-nowrap justify-center md:mt-7 mt-4 md:mb-4 mb-2">
                        <div className='mb-2'>
                        <BrainButtons
                            text={'Private Fork'}
                            className="bg-green"
                            selectedOption={forkStatus}
                            onChange={handlePrivateClick}
                        />
                        </div>
                        <div className='mb-2'>
                        <BrainButtons
                            text={'Shared Fork'}
                            share={true}
                            selectedOption={forkStatus}
                            onChange={handleShareClick}
                        />
                        </div>
                    </div>
                    <div className='mt-3 mb-5 mx-auto flex items-center max-md:flex-col justify-center'>
                            <Label title="Select Brain" className='mr-2' />
                            <CommonSelectInput
                                options={brainOptions}
                                side="top"
                                className={'react-select-container react-select-border-light react-select-sm w-[228px] mr-2'}
                                {...register('type')}
                                onChange={(e) => {
                                    setValue('type', e, { shouldValidate: true })
                                    setSelectedBrain(e)
                                }}
                            />
                            <ValidationError field={'type'} errors={errors}/>
                            <button
                                className="btn btn-black md:mt-0 mt-3"
                                disabled={loading}
                                onClick={handleSubmit(() => {
                                    createNewForkChat({
                                        forkData,
                                        title,
                                        selectedBrain,
                                        closeModal,
                                    })

                                })}>
                                Fork
                            </button>
                        </div>
                        
                    {/*Modal Footer End */}
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default ForkChatModal;
