"use client"
import React, { useCallback, useState } from 'react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import CommonInput from '@/widgets/CommonInput';
import Label from '@/widgets/Label';
import { Popover, PopoverContent, PopoverTrigger } from '../ui/popover';
import CalendarIcon from '@/icons/CalendarIcon';
import 'react-date-range/dist/styles.css';
import 'react-date-range/dist/theme/default.css';
import { Calendar } from 'react-date-range';
import { yupResolver } from '@hookform/resolvers/yup';
import { webProposalAgentSchema, WebProposalAgentSchemaType } from '@/schema/proAgent';
import { useForm, Controller } from 'react-hook-form';
import ValidationError from '@/widgets/ValidationError';
import { ProAgentCode } from '@/types/common';
import { WebProjectProposalFormType } from '@/types/proAgents';

type ProposalProps = {
    setDialogOpen: (open: boolean) => void;
    handleSubmitPrompt: (proAgentData: WebProjectProposalFormType) => void;
}

const defaultValues = {
    clientName: undefined,
    projectName: undefined,
    description: undefined,
    discussionDate: undefined,
    submissionDate: undefined,
    submittedBy: undefined,
    designation: undefined,
    companyName: undefined,
    url: undefined,
    mobile: undefined,
    email: undefined,
    location: undefined,
}

const ProjectProposal = ({setDialogOpen, handleSubmitPrompt }: ProposalProps) => {
    const { register, control, handleSubmit, formState: { errors, isSubmitting } } = useForm<WebProposalAgentSchemaType>({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        resolver: yupResolver(webProposalAgentSchema),
        defaultValues,
    });
    const [isDiscussionPopoverOpen, setIsDiscussionPopoverOpen] = useState(false);
    const [isSubmissionPopoverOpen, setIsSubmissionPopoverOpen] = useState(false);

    const onSubmit = useCallback((data: WebProposalAgentSchemaType) => {
        handleSubmitPrompt({
            code: ProAgentCode.WEB_PROJECT_PROPOSAL,
            url: data.url,
            clientName: data.clientName,
            projectName: data.projectName,
            description: data.description,
            discussionDate: format(data.discussionDate, 'PPP'),
            submittedBy: data.submittedBy,
            designation: data.designation,
            companyName: data.companyName,
            submissionDate: format(data.submissionDate, 'PPP'),
            mobile: data.mobile,
            email: data.email,
            companyLocation: data.location,
        })
        setDialogOpen(false);
    }, []);

    return (
        <div className="qa-form">
            <div className='max-h-[370px] overflow-y-auto'>
                <h2 className='font-bold pb-2 mb-3 border-b'>Project Details</h2>            
                <div className="relative mb-4">
                    <Label title={"Client Name"} htmlFor={"client-name"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        placeholder="Client Name"
                        id="client-name"
                        {...register('clientName')}
                    />
                    <ValidationError errors={errors} field='clientName' />
                </div>
                <div className="relative mb-4">
                    <Label title={"Project Name"} htmlFor={"project-name"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        placeholder="e.g., SEO Campaign: October Clothing Launch"
                        id="project-name"
                        {...register('projectName')}
                    />
                    <ValidationError errors={errors} field='projectName' />
                </div>
                <div className="relative mb-4">
                    <Label title={"Project Description"} htmlFor={"project-description"} className="font-medium text-font-14 mb-1 block" />
                        <textarea
                            id="project-description"
                            placeholder="Description"
                            className="default-form-input"
                            {...register('description')}
                        ></textarea>
                        <ValidationError errors={errors} field='description' />
                </div>

                <h2 className=' font-bold pb-2 mb-3 mt-5 border-b'>Submission Details</h2>
                <div className="relative mb-4">
                    <Label title={"Discussion Date"} className="font-medium text-font-14 mb-1 block"  />
                    <Controller
                        control={control}
                        name='discussionDate'
                        render={({ field}) => (
                            <Popover
                                open={isDiscussionPopoverOpen}
                                onOpenChange={(open) => setIsDiscussionPopoverOpen(open)}
                            >
                                <PopoverTrigger asChild>
                                    <button
                                        className={cn(
                                            "w-full flex items-center px-3 py-3 text-font-14 border border-b9 rounded-md bg-white",
                                            !field.value && "text-muted-foreground"
                                        )}
                                    >
                                        <CalendarIcon width={16} height={16} className="w-4 h-auto fill-b5 mr-2" />
                                        {field.value ? format(field.value, 'PPP') : <span className='text-font-14 text-b6'>DD-MM-YY</span>}
                                    </button>
                                </PopoverTrigger>
                                <PopoverContent className="w-auto p-0" align="start">
                                    <Calendar
                                        onChange={(date) => {
                                            field.onChange(date);
                                            setIsDiscussionPopoverOpen(false); // Close the popover
                                        }}
                                        date={field.value}
                                    />
                                </PopoverContent>
                            </Popover>
                        )}
                    />
                    <ValidationError errors={errors} field='discussionDate' />
                </div>
                <div className="relative mb-4">
                    <Label title={"Submission Date"} className="font-medium text-font-14 mb-1 block"  />
                    <Controller
                        control={control}
                        name='submissionDate'
                        render={({ field }) => (
                            <Popover
                                open={isSubmissionPopoverOpen}
                                onOpenChange={(open) => setIsSubmissionPopoverOpen(open)}
                            >
                                <PopoverTrigger asChild>
                                    <button
                                        className={cn(
                                            "w-full flex items-center px-3 py-3 text-font-14 border border-b9 rounded-md bg-white",
                                            !field.value && "text-muted-foreground"
                                        )}
                                    >
                                        <CalendarIcon width={16} height={16} className="w-4 h-auto fill-b5 mr-2" />
                                        {field.value ? format(field.value, 'PPP') : <span className='text-font-14 text-b6'>DD-MM-YY</span>}
                                    </button>
                                </PopoverTrigger>
                                <PopoverContent className="w-auto p-0" align="start">
                                <Calendar
                                    onChange={(date) => {
                                        field.onChange(date);
                                        setIsSubmissionPopoverOpen(false); // Close the popover
                                    }}
                                    date={field.value}
                                />
                                </PopoverContent>
                            </Popover>
                        )}
                    />
                    <ValidationError errors={errors} field='submissionDate' />
                </div>
                <div className="relative mb-4">
                    <Label title={"Submitted By"} htmlFor={"submitted-by"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        id="submitted-by"
                        {...register('submittedBy')}
                        placeholder='Enter your full name'
                    />
                    <ValidationError errors={errors} field='submittedBy' />
                </div>
                <div className="relative mb-4">
                    <Label title={"Designation"} htmlFor={"designation"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        id="designation"
                        {...register('designation')}
                        placeholder='Enter your job title or role'
                    />
                    <ValidationError errors={errors} field='designation' />
                </div>
                <div className="relative mb-4">
                    <Label title={"Company Name"} htmlFor={"company-name"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        id="company-name"
                        {...register('companyName')}
                        placeholder='Enter the name of your company'
                    />
                    <ValidationError errors={errors} field='companyName' />
                </div>
                <div className="relative mb-4">
                    <Label title={"Company Website"} htmlFor={"company-website"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        id="company-website"
                        {...register('url')}
                        placeholder='Enter your company’s official website'
                    />
                    <ValidationError errors={errors} field='url' />
                </div>
                <div className="relative mb-4">
                    <Label title={"Company Location"} htmlFor={"company-location"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        id="company-location"
                        {...register('location')}
                        placeholder='City, State, Country'
                    />
                    <ValidationError errors={errors} field='location' />
                </div>
                
                <div className="relative mb-4">
                    <Label title={"Contact Number"} htmlFor={"contact-number"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        id="contact-number"
                        {...register('mobile')}
                        placeholder='e.g., +1-234-567-8901'
                        maxLength={18}
                    />
                    <ValidationError errors={errors} field='mobile' />
                </div>
                <div className="relative mb-4">
                    <Label title={"E-mail"} htmlFor={"email-id"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        id="email-id"
                        {...register('email')}
                        placeholder='yourname@company.com'
                    />
                    <ValidationError errors={errors} field='email' />
                </div>

                <div className="relative mb-4 flex gap-2">
                    <button className="btn btn-outline-black text-font-14" onClick={handleSubmit(onSubmit)} disabled={isSubmitting}>
                        Run Agent
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ProjectProposal;