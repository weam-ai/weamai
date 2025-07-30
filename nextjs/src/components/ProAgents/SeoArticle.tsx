import React, { useState, useCallback, useEffect } from 'react';
import Label from '@/widgets/Label';
import Select, { StylesConfig, MultiValue } from 'react-select';
import ChipInput from "material-ui-chip-input";
import { makeStyles } from '@material-ui/core';
import Close from "@/icons/Close";
import CommonInput from '@/widgets/CommonInput';
import useProAgent from '@/hooks/conversation/useProAgent';
import ValidationError from '@/widgets/ValidationError';
import { useForm, Controller } from 'react-hook-form';
import { seoAgentSchema, SeoAgentSchemaType } from '@/schema/proAgent';
import { yupResolver } from '@hookform/resolvers/yup';
import { ProAgentCode } from '@/types/common';
import { ProAgentDataType } from '@/types/chat';
import { SelectOption } from '@/types/proAgents';
import countries from '@/utils/countrylist';

const useStyles = makeStyles((theme) => ({
    inputRoot: {
        // Custom styles for the input container
        borderRadius: '5px',
        border: '1px solid #bfbfbf',
        backgroundColor: '#fff',
        '&:hover': {
            borderColor: '#aaa',
        },
    },
    input: {
        // Custom styles for the input field
        color: '#333',
        fontSize: '14px',
        padding: '15px 15px',
        '&::placeholder': {
            color: '#111',
        },
    },
    chip: {
        // Custom styles for the chip
        backgroundColor: '#6637EC',
        color: '#fff',
        margin: '7px 6px',
        '&:hover': {
            backgroundColor: '#bfbfbf',
            color: '#000',
        },
    },
    chipDeleteIcon: {
        // Custom styles for the delete icon
        color: '#ff1744',
    },
}));

const customStyles: StylesConfig = {
    option: (provided, state) => ({
        ...provided,
        backgroundColor: state.isFocused ? "#f5f5f5" : "#ffffff", // Highlight option on hover or when selected
        color: "#000", 
        cursor: "pointer",
        fontSize: "14px",
        pointerEvents: "auto",
    }),
    menu: (provided) => ({
        ...provided,
        zIndex: 9999,
    }),
    menuPortal: (base) => ({
        ...base,
        zIndex: 9999, // Ensure it's above other elements
    }),
    control: (provided) => ({
        ...provided,
        borderColor: "#888888",
        cursor: "pointer",
    }),
};

type SeoArticleProps = {
    setDialogOpen: (open: boolean) => void;
    handleSubmitPrompt: (proAgentData: ProAgentDataType) => void;
}

const defaultValues = {
    projectName: undefined,
    webUrl: undefined,
    keywords: [],
    location: [],
    audience: undefined,
    summary: undefined,
}

const SeoArticle = ({setDialogOpen, handleSubmitPrompt }: SeoArticleProps) => { 
    const [chips, setChips] = useState<string[]>([]);
    const [keywordLoader, setKeywordLoader] = useState(true);
    const { register, handleSubmit, formState: { errors, isSubmitting }, setValue, control, watch, getValues } = useForm<SeoAgentSchemaType>({
        mode: 'onSubmit',
        resolver: yupResolver(seoAgentSchema),
        defaultValues
    });

    const classes = useStyles();
    const { 
        generateAudienceAndSummary, 
        isLoading,
    } = useProAgent();

    const handleDeleteChip = useCallback((chipToDelete: string) => {
        setChips((prevChips: string[]) => prevChips.filter((chip) => chip !== chipToDelete));
    }, [chips]);

    const onSubmit = useCallback((data: SeoAgentSchemaType) => {
        handleSubmitPrompt({
            code: ProAgentCode.SEO_OPTIMISED_ARTICLES,
            url: data.url as string,
            projectName: data.projectName as string,
            keywords: data.keywords as string[],
            location: data.location as string[],
            audience: data.audience as string,
            summary: data.summary as string,
        });
        setDialogOpen(false);     
    }, []);
    const [showLoader, setShowLoader] = useState(false);

    const onKeywordGenerate = useCallback(async () => {
        setShowLoader(true);
        const response = await generateAudienceAndSummary({
            projectName: getValues('projectName') as string,
            keywords: getValues('keywords') as string[],
            location: getValues('location') as SelectOption[],
            url: getValues('url') as string,
        });
        setShowLoader(false);
        if (response) {
            const { business_summary, target_audience } = response.data;
            setValue('summary', business_summary);
            setValue('audience', target_audience);
        }
    }, [generateAudienceAndSummary]);

    const watchFields = watch(['projectName', 'url', 'keywords', 'location']);

    useEffect(() => {
        const isValid = watchFields.every((field) => {
            if (Array.isArray(field)) return field.length > 0;
            if (typeof field === 'string') return field.trim() !== '';
            return field !== undefined && field !== null;
        });
        setKeywordLoader(!isValid);
    }, [watchFields]);
    
    return (
        <div className="qa-form">
            <div className='max-h-[370px] overflow-y-auto'>
                <div className="relative mb-4">
                    <Label title={"Name of the Project"} htmlFor={"project-name"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        type="text"
                        placeholder="e.g., SEO Campaign: October Clothing Launch"
                        className="default-form-input"
                        id="project-name"
                        {...register('projectName')}
                    />
                    <ValidationError errors={errors} field={'projectName'}/>
                </div>
                <div className="relative mb-4">
                    <Label title={"Website URL "} htmlFor={"web-url"} className="font-medium text-font-14 mb-1 block" />
                    <CommonInput
                        type="url"
                        placeholder="e.g., https://www.creativeagency.com"
                        className="default-form-input"
                        id="web-url"
                        {...register('url')}
                    />
                    <ValidationError errors={errors} field={'url'}/>
                </div>
                <div className="relative mb-4">
                    <Label title={"Targeted Keyword"} htmlFor={"keywords"} className="font-medium text-font-14 mb-1 block" />
                    <Controller
                        control={control}
                        name='keywords'
                        render={({ field }) => (
                            <ChipInput
                                {...field}
                                value={Array.isArray(field.value) ? field.value : []}
                                required
                                className="w-full default-form-input !p-0 "
                                id="keywords"
                                placeholder='Type and press enter, tab or comma to add tags' 
                                disableUnderline
                                newChipKeys={["Enter", "Tab", ',']}
                                classes={{
                                    root: classes.inputRoot,
                                    input: classes.input,
                                    chip: classes.chip,
                                }}
                                onAdd={(chip) => field.onChange([...(Array.isArray(field.value) ? field.value : []), chip])}
                                onDelete={(chipToDelete) => {
                                    const updated = (Array.isArray(field.value) ? field.value : []).filter((chip) => chip !== chipToDelete);
                                    field.onChange(updated);
                                }}
                            />
                        )}
                    />
                    <ValidationError errors={errors} field={'keywords'}/>
                </div>
                <div className="relative mb-4">
                    <Label title={"Location"} htmlFor={"location"} className="font-medium text-font-14 mb-1 block" />
                    <Select 
                        options={countries} 
                        menuPlacement="auto"
                        // menuPortalTarget={document.body} 
                        styles={customStyles}                        
                        isMulti
                        id="location" 
                        className="react-select-container" 
                        classNamePrefix="react-select"
                        {...register('location')}
                        onChange={(e: MultiValue<SelectOption>) => {
                            setValue('location', e, { shouldValidate: true, shouldDirty: true });
                        }}
                    />
                    <ValidationError errors={errors} field={'location'}/>
                </div>
                <div className="col-span-12 relative mb-4 flex gap-x-1 flex-wrap">
                    {chips.map((chip: string, index: number) => (
                    <div key={index} className="text-font-14 px-3 py-1 bg-b11 rounded-md relative mt-2">
                        <span>{chip}</span>
                        <span className="cursor-pointer" onClick={() => handleDeleteChip(chip)}>
                            <Close className="w-2 h-auto fill-b3 absolute right-[-2px] top-[-2px]" onClick={() => handleDeleteChip(chip)} />
                        </span>
                    </div>
                    ))}
                </div>
                <div className="grid grid-cols-12 gap-x-5 bg-b12 p-4 rounded-md mb-2">
                    <div className="col-span-12 lg:col-span-12 relative mb-4">
                        <Label title={"Targeted Audience"} htmlFor={"targeted-audience"} className="font-medium text-font-14 mb-1 block" />
                        <CommonInput
                            type="text"
                            placeholder="Describe your targeted audience"
                            className="default-form-input"
                            id="targeted-audience"
                            {...register('audience')}
                        />
                        <ValidationError errors={errors} field={'audience'}/>
                    </div>
                    <div className="col-span-12 lg:col-span-12 relative mb-4">
                        <Label title={"Business Summary"} htmlFor={"business-summary"} className="font-medium text-font-14 mb-1 block" />
                        <textarea
                            placeholder="Summarize your business"
                            className="default-form-input"
                            id="business-summary"
                            {...register('summary')}
                        />
                        <ValidationError errors={errors} field={'summary'}/>
                    </div>
                    <div className="col-span-12 lg:col-span-12 relative">
                        <button className="btn btn-black text-font-14" disabled={keywordLoader || isLoading} onClick={onKeywordGenerate}>Generate with AI </button>
                        {showLoader && (
                            <div className="inline-block align-middle ml-2 w-[20px] h-[20px] animate-spin border-2 border-b-2 border-blue rounded-full border-t-b10"></div>
                        )}
                    </div>
                </div>
                <div className="relative mb-4 flex gap-2">
                    <button className="btn btn-outline-black text-font-14" onClick={handleSubmit(onSubmit)} disabled={isSubmitting || isLoading}>
                        Run Agent
                    </button>
                </div>
            </div>

        </div>
    );
};

export default SeoArticle;
