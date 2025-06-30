import React, { useState, useCallback } from 'react';
import ArrowBack from '@/icons/ArrowBack';
import { RadioGroup, RadioGroupItem } from '../ui/radio-group';
import Label from '@/widgets/Label';
import CommonInput from '@/widgets/CommonInput';
import Select, { StylesConfig } from 'react-select';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { videoCallSchema } from '@/schema/proAgent';
import ValidationError from '@/widgets/ValidationError';
import Toast from '@/utils/toast';
import useFileDropZone from '@/hooks/common/useFileDropZone';
import { FILE_UPLOAD_FOLDER } from '@/utils/constant';
import FileUploadProgress from '../Loader/FileUploadProgress';
import { ProAgentCode } from '@/types/common';
import { SALES_CALL_ANALYZER_API_CODE } from '@/types/proAgents';
import TooltipIcon from '@/icons/TooltipIcon';
import AudioUploadIcon from '@/icons/AudioUploadIcon';
import DocumentIcon from '@/icons/DocumentIcon';

type SalesProps = {
    setDialogOpen: (open: boolean) => void;
    handleSubmitPrompt: (proAgentData: { code: ProAgentCode, audio_url: string, prompt?: string }) => void;
}

const isFathomUrl = (url: string) => {
    const regex = /^https:\/\/fathom\.video\//;
    return regex.test(url);
};
  
export const ALLOWED_AUDIO_FILE_TYPES = [
    '.m4a',
] as const;

export const ALLOWED_DOCUMENT_FILE_TYPES = [
    '.txt',
] as const;

const customStyles: StylesConfig = {
    option: (provided, state) => ({
        ...provided,
        backgroundColor: state.isFocused ? '#f5f5f5' : '#ffffff',
        color: '#000',
        cursor: 'pointer',
        fontSize: '14px',
        pointerEvents: 'auto',
    }),
    menu: (provided) => ({
        ...provided,
        zIndex: 9999,
    }),
    menuPortal: (base) => ({
        ...base,
        zIndex: 9999,
    }),
    control: (provided) => ({
        ...provided,
        borderColor: '#888888',
        cursor: 'pointer',
    }),
};

const SalesCall = ({ handleSubmitPrompt, setDialogOpen }: SalesProps) => {
    // first step radio group state
    const [radioSelected, setRadioSelected] = useState<Record<string, boolean>>({
        upload: true,
        fathom: false,
        transcript: false,
    });

    // second step radio group state
    const [productUrlSelected, setProductUrlSelected] = useState<Record<string, boolean>>({
        url: true,
        document: false,
    });

    // radio group selection data
    const [radioSelectionData, setRadioSelectionData] = useState<Record<string, string>>({
        fathom: '',
        transcript: '',
        product_url: '',
    });

    const [step, setStep] = useState(1);
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    const SelectPrompts = [
        { value: 'default-prompt', label: 'Default Prompt' },
        { value: 'custom-prompt', label: 'Custom Prompt' },
    ];

    const DEFAULT_PROMPT = `You are the "Sales Call Analyzer," an advanced analytical tool designed to evaluate and break down recorded sales call transcripts for comprehensive insights.

    Page Analysis from website: Based on the website content and call transcript, please analyze the call that took place between the sales team and the prospect. Provide a detailed evaluation of the call, including demographic details of the prospect, sales team performance metrics, and actionable recommendations for improvement. Include an overall effectiveness score on a scale of 1 to 10 reflecting the quality and success of the sales team's performance. Include a breakdown of strengths, weaknesses, and suggestions for enhancing the sales strategy. based on the Page Analysis, sales person forgot which product or service he forgot to mention to client in call: Note:- Provide only the evaluation without any additional or miscellaneous information.
    
    Primary Objectives
    Analyze sales call transcripts, even when participants are not explicitly identified, for both qualitative insights and quantitative metrics.
    Provide an overall effectiveness score on a 1-to-10 scale that reflects the quality and success of the sales team's performance during the call.
    Offer a comprehensive breakdown of the call, identifying strengths, weaknesses, and actionable suggestions for improvement.
    Dynamically infer speaker roles based on context, ensuring clarity in cases where participants are not predefined or explicitly labeled.
    Criteria for Analysis
    Extract and analyze the following factors during the evaluation of a sales call transcript, ensuring demographic data of the prospect and sales performance metrics are identified:
    
    1. Prospect's Demographic Details:
    Team Size: Infer the size of the prospect’s team from context, if mentioned.
    Work Volume: Assess the typical amount or scale of work the prospect's team handles.
    Location: Identify the location of the prospect or their business, if disclosed.
    Previous Experience: Determine if the prospect has used similar services in the past and evaluate their satisfaction level (positive or negative feedback).
    Likelihood of Closing: Based on the content and tone of the conversation, provide an estimate of deal closure probability.
    Website: Extract the URL of the prospect’s business, if mentioned.
    Business Summary: Provide a concise summary of the prospect’s business, including their model, services/products offered, and overarching goals.
    2. Sales Team Performance:
    Evaluate the sales team based on the following key factors:
    
    Responsiveness: Were the sales representatives able to effectively and confidently address the prospect’s queries? Identify instances of thorough answers or incomplete responses.
    Satisfaction: Did the prospect verbally or contextually indicate satisfaction or dissatisfaction with the sales team’s responses and solutions?
    Engagement: Assess the level of engagement from the prospect. Did they ask relevant questions, seem interested in follow-ups, or express clarity in intent? High engagement often indicates strong interest.
    Edge Case Adaptation
    In scenarios where speaker identification is unclear:
    
    Dynamic Role Assignment: Use contextual language cues to identify the roles of different speakers (e.g., sales representative, prospect, or other team members). Distribute roles based on the flow and logical structure of the conversation.
    Ambiguity Resolution: When uncertain, infer roles and participation using natural language understanding and indicate any assumptions made. Keep the analysis coherent.
    Multiple Participants: Handle transcripts with multiple participants by distinguishing unique voices and listing speaker roles accordingly to ensure all contributions are evaluated.
    Handling Complex Scenarios
    For scenarios where information may be fragmented, incomplete, or ambiguous, you should:
    
    Cross-reference Data: Synthesize information from different parts of the transcript to extract demographic details or strengthen role identification.
    Business Profiling: Combine fragmented details to develop a well-rounded business summary for the prospect where explicit information is missing.
    Contextual Inference: Make logical inferences about speaker intent, engagement, and conversational flow based on tone, phrasing, and context. Clearly indicate any assumptions.
    Sales Opportunity Analysis
    Identify potential sales opportunities by:
    
    Product/Service Gap Analysis: Identify products/services from website content that weren't discussed during the call
    Upselling Detection: Look for:
    Premium feature mentions that weren't explored
    Indications of budget flexibility
    Pain points that premium solutions could address
    Cross-selling Indicators: Monitor:
    Related product needs mentioned by prospect
    Complementary service opportunities
    Business challenges that multiple products could solve
    Opportunity Scoring: Rate each opportunity on:
    Relevance to prospect's needs (1-5)
    Likelihood of conversion (1-5)
    Potential revenue impact (1-5)
    Present the analysis in the following organized format: Give Little Descrption of the Call between both the parties
    
    1. Summary
    Provide a high-level overview of the call outcome (e.g., tone of call, progress in the sales journey, and overall impression of the interaction).
    2. Call Rating (1-10)
    Deliver a single numerical score summarizing the overall effectiveness of the call, considering factors such as engagement quality, responsiveness, upselling or cross-selling tried by the agent or not and likelihood of deal closure.
    3. Recommendations for Improvement
    List tailored suggestions to enhance sales tactics, address weaknesses, and build on strengths observed during the call. Ensure recommendations are actionable and specific (e.g., "Streamline responses to frequently asked questions about pricing").
    4. Key Insights
    Provide detailed notes on the following components:
    
    Demographic Information: Include team size, work volume, location, business website, previous experiences, likelihood of closing, and business summary.
    Performance Evaluation: Highlight aspects of responsiveness, prospect satisfaction, and engagement.
    Other Notable Findings: Mention any additional insights relevant to the prospect’s needs or sales strategy effectiveness.
    5. Sales Opportunity Analysis
    Provide detailed notes on the following components:
    
    Product/Service Gap: Identify products or services from the website that weren't discussed during the call.
    Upselling/Cross-selling Opportunities: Highlight potential areas for upselling or cross-selling based on the prospect's needs and the website content.
    Opportunity Scoring: Rate each opportunity based on relevance, likelihood of conversion, and potential revenue impact.
    Important Considerations
    Actionable Insights: Ensure your output provides usable, specific, and strategic recommendations aimed at improving future sales calls. Avoid generic advice.
    Thoroughness Over Ambiguity: Address incomplete or ambiguous details constructively while maintaining transparency in your analysis (e.g., "The participant's role was inferred based on statements indicating decision-making authority").
        Adaptability: Be prepared to work with a variety of transcript formats, conversational styles, and levels of detail. Ensure your analysis remains consistent despite variable data quality. By adhering to these guidelines, provide sales teams with actionable insights and practical evaluations that enable them to close deals more effectively and build stronger engagements with prospects.`;
        
    const [selectedPrompt, setSelectedPrompt] = useState(SelectPrompts[0]);
    const [promptText, setPromptText] = useState(DEFAULT_PROMPT);
    const [isReadOnly, setIsReadOnly] = useState(true);
    const {
        handleFileChange,
        fileLoader,
        fileProgress,
        uploadedFiles,
        uploadedDocuments,
        handleDocumentChange,
        metadata,
        handleDragOver,
        handleDragEnter,
        handleDragLeave,
        handleDrop,
        audioDropRef,
        docDropRef
    } = useFileDropZone({ folder: FILE_UPLOAD_FOLDER.SALES_CALL_AGENT });

    const { register, handleSubmit, setValue, formState: { errors, isSubmitting: formSubmitting } } = useForm({
        resolver: yupResolver(videoCallSchema),
        defaultValues: { url: 'Decode Every Call. Close More Deals.', prompt: '' },
        mode: 'onSubmit'
    });

    const handleRadioChange = useCallback((option: string) => {
        setRadioSelected((prev: Record<string, boolean>) => Object.fromEntries(
            Object.keys(prev).map(key => [key, key === option])
        ) as typeof radioSelected);
    }, [radioSelected]);

    const handleProductUrlChange = useCallback((option: string) => {
        setProductUrlSelected((prev: Record<string, boolean>) => Object.fromEntries(
            Object.keys(prev).map(key => [key, key === option])
        ) as typeof productUrlSelected);
    }, [productUrlSelected]);

    const handleRadioSelectionData = useCallback((option: string, value: string) => {
        setRadioSelectionData((prev: Record<string, string>) => ({
            ...prev,
            [option]: value,
        }));
    }, [radioSelectionData]);

    const handleSave = useCallback(() => {
        const { fathom, transcript } = radioSelectionData;
        const hasFathom = fathom.trim() !== '';
        const hasTranscript = transcript.trim() !== '';
        const hasUpload = uploadedFiles.length > 0;

        if (!hasFathom && !hasTranscript && !hasUpload) {
            Toast('Please provide a fathom url or upload a transcript.', 'error');
            return;
        }

        if (hasFathom && !hasTranscript && !hasUpload && !isFathomUrl(fathom)) {
            Toast('Please enter a valid public Fathom URL.', 'error');
            return;
        }
        setStep(2);
    }, [radioSelectionData, uploadedFiles]);

    const BacktoStep1 = useCallback(() => {
        setStep(1);
    }, [radioSelectionData, uploadedFiles]);

    const handleStep2Save = useCallback(async () => {
        const { product_url } = radioSelectionData;
        const hasProductUrl = product_url.trim() !== '';
        const hasUpload = uploadedDocuments.length > 0;
        if (!hasProductUrl && !hasUpload) {
            Toast('Please provide a product/service URL or upload a document.', 'error');
            setIsSubmitting(false);
            return;
        }
        
        if(selectedPrompt.value === 'default-prompt') {
            setPromptText(DEFAULT_PROMPT);
            setValue('prompt', DEFAULT_PROMPT);
        }else if(selectedPrompt.value === 'custom-prompt' && promptText === DEFAULT_PROMPT) {
            setPromptText('');
            setValue('prompt', '');
        }else if(selectedPrompt.value === 'custom-prompt' && promptText !== DEFAULT_PROMPT) {
            setPromptText(promptText);
            setValue('prompt', promptText);
        }
        setStep(3);
    }, [radioSelectionData, uploadedDocuments, DEFAULT_PROMPT, selectedPrompt, promptText, setValue]);

    const BacktoStep2 = useCallback(() => {
        setStep(2);
    }, []);

    const handleRunAgent = async () => {
        setIsSubmitting(true);
        
        const serviceCodeMap: Record<string, string> = {
            fathom: SALES_CALL_ANALYZER_API_CODE.FATHOM,
            transcript: SALES_CALL_ANALYZER_API_CODE.TRANSCRIPT,
        }
        const productCodeMap: Record<string, string> = {
            url: SALES_CALL_ANALYZER_API_CODE.URL,
            document: SALES_CALL_ANALYZER_API_CODE.DOC,
        }
        const selectedKey = Object.keys(radioSelected).find(key => radioSelected[key]);;
        const selectedProductKey = Object.keys(productUrlSelected).find(key => productUrlSelected[key]);
        const serviceCode = serviceCodeMap[selectedKey as keyof typeof serviceCodeMap] || SALES_CALL_ANALYZER_API_CODE.AUDIO;
        const productCode = productCodeMap[selectedProductKey as keyof typeof productCodeMap] || SALES_CALL_ANALYZER_API_CODE.DOC;
        /**
         *  Reason for access first index of uploadedFiles is because we are using single file upload
         *  and we are using common file upload hook which return array of files
         *  
         */
        const senderData = {
            code: ProAgentCode.SALES_CALL_ANALYZER,
            service_code: serviceCode,
            product_summary_code: productCode,
            audio_url: uploadedFiles?.length ? uploadedFiles[0]?.url : radioSelectionData[selectedKey as keyof typeof radioSelectionData],
            product_info: uploadedDocuments?.length ? uploadedDocuments[0]?.url : radioSelectionData.product_url,
            url: 'Decode Every Call. Close More Deals.', 
            audio_file_metadata: uploadedFiles?.length ? uploadedFiles : [],
            document_file_metadata: uploadedDocuments?.length ? uploadedDocuments : [],
            ...(selectedPrompt.value === 'custom-prompt' && { prompt: promptText }),
        }
        handleSubmitPrompt(senderData);
        setDialogOpen(false);
    };

    return (
        <div className="qa-form">
            {step === 1 && (
            <>
                <div className="relative mb-4">
                    {/* Main Radio Group */}
                    <RadioGroup className="my-3 flex items-center max-md:flex-wrap" value={radioSelected.upload ? "upload" : radioSelected.fathom ? "fathom" : "transcript"} onValueChange={handleRadioChange}>
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="upload" id="zoom-audio" />
                            <Label className="mb-0 text-font-14" htmlFor="zoom-audio" title="Upload Zoom Audio" required={radioSelected.upload}>Upload Zoom Audio</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="fathom" id="fathom-url-step" />
                            <Label className="mb-0 text-font-14" htmlFor="fathom-url-step" title="Provide a Fathom URL" required={radioSelected.fathom}>Provide a Fathom URL</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="transcript" id="existing-transcript" />
                            <Label className="mb-0 text-font-14" htmlFor="existing-transcript" title="Enter Existing Transcript" required={radioSelected.transcript}>Upload/Enter Existing Transcript</Label>
                        </div>
                    </RadioGroup>

                    {/* Conditionally Render Input Areas */}
                    {radioSelected.upload && (
                        <div 
                            className='pt-1' 
                            ref={audioDropRef} 
                            onDragOver={handleDragOver} 
                            onDragEnter={handleDragEnter} 
                            onDragLeave={handleDragLeave} 
                            onDrop={(e: React.DragEvent<HTMLDivElement>) => handleDrop(e, false)}
                        >
                            <div className='my-3 relative'>
                                <div className='w-full p-8 border border-b10 rounded-lg border-dashed flex items-center justify-center flex-col'>
                                    <AudioUploadIcon className="mx-auto w-16 h-auto my-5 fill-b2" height={64} width={64} />
                                    <h3 className='text-font-14 font-bold'>Drag & drop files or Browse</h3>
                                    <p className='text-font-14'>Supported audio file in .m4a format.</p>
                                </div>

                                <input 
                                    type="file" 
                                    className='border border-b-4 rounded-lg text-center cursor-pointer px-3 py-5 w-full text-font-14 absolute left-0 top-0 h-full opacity-0' 
                                    onChange={handleFileChange} 
                                    accept={ALLOWED_AUDIO_FILE_TYPES.join(',')}
                                />
                            </div>
                            {fileLoader && (
                                <FileUploadProgress fileName={metadata[0]?.name}  progress={fileProgress} loading={fileLoader} />
                            )}
                            {
                                uploadedFiles.length > 0 && (
                                    <FileUploadProgress fileName={uploadedFiles[0]?.name} loading={false} />
                                )
                            }
                        </div>
                    )}

                    {radioSelected.fathom && (
                        <div className='pt-1'>
                            <div className='mt-3'>
                                <Label title="Fathom URL" htmlFor="fathom-URL" />
                                <CommonInput
                                    type="text"
                                    placeholder="Enter your public Fathom URL here (e.g., https://app.fathom.video/v/sample-url)."
                                    className="default-form-input"
                                    id="fathom-URL"
                                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleRadioSelectionData('fathom', e.target.value)}
                                    value={radioSelectionData.fathom}
                                />
                            </div>
                        </div>
                    )}

                    {radioSelected.transcript && (
                        <div className='pt-1'>
                            <div className="transcript-text mt-3">
                                <Label title="Transcript" htmlFor="transcript" />
                                    <textarea
                                        id="transcript"
                                        placeholder="Enter your transcript here."
                                        className="default-form-input"
                                        onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleRadioSelectionData('transcript', e.target.value)}
                                        value={radioSelectionData.transcript}
                                    ></textarea>
                            </div>
                        </div>
                    )}
                </div>
                
                <div className="relative mb-4 flex gap-2 justify-center">
                    <button className="btn btn-outline-black text-font-14" onClick={handleSave} disabled={fileLoader}>
                        Next
                    </button>
                </div>
            </>
            )}
            {step === 2 && (
            <>
                <div className='relative mb-4'>
                    <RadioGroup className="my-3 flex items-center max-md:flex-wrap" value={productUrlSelected.url ? "url" : productUrlSelected.document ? "document" : "default"} onValueChange={handleProductUrlChange}>
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="url" id="context-1" />
                            <Label className="mb-0 text-font-14" htmlFor="context-1" title="Enter Product/Service URL" required={productUrlSelected.url}>Enter Product/Service URL</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                            <RadioGroupItem value="document" id="context-2" />
                            <Label className="mb-0 text-font-14" htmlFor="context-2" title="Upload Product/Service Document" required={productUrlSelected.document}>Upload Product/Service Document</Label>
                        </div>
                    </RadioGroup>

                    {productUrlSelected.url && (
                        <div>
                            <Label title="Enter Product/Service URL" htmlFor="web-url" />
                            <input
                                type="url"
                                id="web-url"
                                placeholder='Enter your product/service website URL (e.g., https://example.com).'
                                className="default-form-input"
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                                    handleRadioSelectionData('product_url', e.target.value);
                                    setValue('url', e.target.value);
                                }}

                            />
                            <p className='text-font-12 text-b6 mt-2 flex items-start'>
                                <TooltipIcon className="inline-block mr-1 fill-b5 w-4 mt-1 h-auto" width={16} height={16} />
                                We`ll scrape this URL to check if your sales call aligns with your offerings and to detect upselling or cross-selling opportunities.</p>
                        </div>
                    )}

                    {productUrlSelected.document && (
                        <div 
                            ref={docDropRef} 
                            onDragOver={handleDragOver} 
                            onDragEnter={handleDragEnter} 
                            onDragLeave={handleDragLeave} 
                            onDrop={(e: React.DragEvent<HTMLDivElement>) => handleDrop(e, true)}
                        >
                            <Label title="Upload Product/Service Document" htmlFor="web-url" />
                            <div className='relative'>
                                <div className='w-full p-8 border border-b10 rounded-lg border-dashed flex items-center justify-center flex-col'>
                                    <DocumentIcon className="mx-auto w-12 h-auto my-5 fill-b2" height={48} width={48} />
                                    <h3 className='text-font-14 font-bold'>Drag & drop files or Browse</h3>
                                    <p className='text-font-14'>Supported document file in .txt format.</p>
                                </div>
                                <input 
                                    type="file" 
                                    className='border border-b-4 rounded-lg text-center cursor-pointer px-3 py-5 w-full text-font-14 absolute left-0 top-0 h-full opacity-0' 
                                    onChange={handleDocumentChange} 
                                    accept={ALLOWED_DOCUMENT_FILE_TYPES.join(',')}
                                />
                            </div>
                            
                            {fileLoader && (
                                <FileUploadProgress fileName={metadata[0]?.name}  progress={fileProgress} loading={fileLoader} />
                            )}
                            {
                                uploadedDocuments.length > 0 && (
                                    <FileUploadProgress fileName={uploadedDocuments[0]?.name} loading={false} />
                                )
                            }
                        </div>
                    )}                
                </div>
                <div className="relative mb-4 flex gap-2 justify-center">
                    <button className="btn btn-outline-black text-font-14 flex [&>svg]:hover:fill-white" onClick={BacktoStep1}>
                        <ArrowBack width={16} height={16} className="fill-b2 w-[16px] h-auto mr-1" /> Back
                    </button>
                    <button className="btn btn-outline-black text-font-14" onClick={handleStep2Save} disabled={fileLoader || isSubmitting}>
                        Next
                    </button>
                </div>
            </>
            
            )}
            {step === 3 && (
            <>
                <div className="prompt">
                    <div className="relative mb-4">
                        <Label title={'Select Prompt'} htmlFor={'prompt'} />
                        <Select 
                            options={SelectPrompts} 
                            menuPlacement="auto"
                            defaultValue={selectedPrompt}
                            styles={customStyles}
                            id="prompt" 
                            className="react-select-container" 
                            classNamePrefix="react-select"
                            onChange={(option: any) => {
                                if (!option) return;
                                const value = option.value;

                                if (value === 'custom-prompt') {
                                    if (promptText === DEFAULT_PROMPT) {
                                        setPromptText('');
                                        setValue('prompt', '');
                                    }
                                    setSelectedPrompt(SelectPrompts[1]);
                                    setIsReadOnly(false);     
                                } else {
                                    setPromptText(DEFAULT_PROMPT);
                                    setSelectedPrompt(SelectPrompts[0]);
                                    setIsReadOnly(true);      
                                }
                            }}
                        />
                    </div>
                    <div className="relative mb-4">
                        <Label title={'Prompt'} htmlFor={'prompt'} />
                        <textarea
                            placeholder="Your custom prompts"
                            onChange={(e) => {
                                if (!isReadOnly) {
                                    setPromptText(e.target.value);
                                    setValue('prompt', e.target.value);
                                }
                            }}
                            className="default-form-input !min-h-32"
                            id="business-summary"
                            readOnly={isReadOnly}
                            value={promptText}
                            name="prompt"
                        />
                        <ValidationError errors={errors} field='prompt' />
                    </div>
                </div>
                <div className="relative mb-4 flex gap-2 justify-center">
                    <button className="btn btn-outline-black text-font-14 flex [&>svg]:hover:fill-white" onClick={BacktoStep2}>
                        <ArrowBack width={16} height={16} className="fill-b2 w-[16px] h-auto mr-1" /> Back
                    </button>
                    <button className="btn btn-outline-black text-font-14" 
                        onClick={handleSubmit(handleRunAgent)}
                        disabled={formSubmitting || isSubmitting || fileLoader}
                    >
                        Run Agent
                    </button>
                </div>
            </>
            
            )}
        </div>
    );
};

export default SalesCall;