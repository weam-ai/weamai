
import { useState, useCallback, memo } from 'react';
import Label from '@/widgets/Label';
import HuggingIcon from '../../../public/hugging-logo.svg'
import { Switch } from '../ui/switch';
import { customSelectStyles } from '@/utils/customStyles';
import { Slider } from '../ui/slider';
import CommonInput from '@/widgets/CommonInput';
import Image from 'next/image';
import useHuggingFace from '@/hooks/aiModal/useHuggingFace';
import ValidationError from '@/widgets/ValidationError';
import CommonSelectInput from '@/widgets/CommonSelectInput';
import {
   Tooltip,
   TooltipContent,
   TooltipProvider,
   TooltipTrigger,
} from '@/components/ui/tooltip';
import { useSelector } from 'react-redux';
import { RootState } from '@/lib/store';
const taskCode = {
   TEXT_GENERATION: 'TEXT_GENERATION',
   IMAGE_GENERATION: 'IMAGE_GENERATION'
}

const TaskType = [
   // { value: 'audio-classification', label: 'Audio Classification', isDisabled: true },
   // { value: 'automatic-speech-recognition', label: 'Automatic Speech Recognition', isDisabled: true },
   // { value: 'custom', label: 'Custom', isDisabled: true },
   // { value: 'feature-extraction', label: 'Feature Extraction', isDisabled: true },
   // { value: 'fill-mask', label: 'Fill Mask', isDisabled: true },
   // { value: 'image-classification', label: 'Image Classification', isDisabled: true },
   // { value: 'image-segmentation', label: 'Image Segmentation', isDisabled: true },
   // { value: 'image-text-to-text', label: 'Image-Text-to-Text', isDisabled: true },
   // { value: 'object-detection', label: 'Object Detection', isDisabled: true },
   // { value: 'question-answering', label: 'Question Answering', isDisabled: true },
   // { value: 'sentence-embeddings', label: 'Sentence Embeddings', isDisabled: true },
   // { value: 'sentence-similarity', label: 'Sentence Similarity', isDisabled: true },
   // { value: 'sentence-ranking', label: 'Sentence Ranking', isDisabled: true },
   // { value: 'summarization', label: 'Summarization', isDisabled: true },
   // { value: 'table-question-answering', label: 'Table Question Answering', isDisabled: true },
   // { value: 'text-classification', label: 'Text Classification', isDisabled: true },
   { value: 'text-generation', label: 'Text Generation', code: taskCode.TEXT_GENERATION },
   { value: 'text-to-image', label: 'Text-to-Image', code: taskCode.IMAGE_GENERATION, },
   // { value: 'token-classification', label: 'Token Classification', isDisabled: true },
   // { value: 'translation', label: 'Translation', isDisabled: true },
   // { value: 'zero-shot-classification', label: 'Zero Shot Classification', isDisabled: true },
   // { value: 'conversational', label: 'Conversational [Deprecated]', isDisabled: true },
   // { value: 'text2text-generation', label: 'Text-to-Text Generation [Deprecated]', isDisabled: true },
]

const APITypeOptions = [
   { value: 'OpenAI Compatible API', label: 'OpenAI Compatible API' },
]

const HuggingFaceAPIInput = ({ register, errors, configs }) => {
   return (
      <div className={`relative mb-4`}>
         <label
            className="font-semibold mb-2 inline-block"
         >
            <span className="w-7 h-7 rounded-full bg-b11 inline-flex items-center justify-center me-2.5 align-middle">
               <Image
                  src={HuggingIcon}
                  alt={'Hugging Face Auth Token'}
                  width={16}
                  height={16}
                  className="w-5 h-5 object-contain object-center inline-block"
               />
            </span>
            {`Hugging Face Auth Token`}
            <span className="text-red px-1">*</span>
          </label>
          <div className="gap-2.5 flex">
               <CommonInput
                  {...register('key')}
                  placeholder={'hf_xxxxxxxxxxxxxxxxxx'}
                  defaultValue={configs?.apikey ? 'hf_xxxxxxxxxxxxxxxxxx' : ''}
               />         
          </div>
          <ValidationError errors={errors} field={'key'} />
      </div>
   );
}

const HuggingFaceModelProvider = ({ configs }) => {
   const [extraConfig, setExtraConfig] = useState({
      value: 8096,
      frequencyPenalty: 1,
      topK: 10,
      topP: 0.95,
      typicalP: 0.95,
      repetitionPenalty: 1.03,
      temperature: 0.7,
      numInference: 15,
      gScale: 3
   });

   const [switchConfig, setSwitchConfig] = useState({
      tool: false,
      sample: false,
   });
   
   const [isExtraConfigVisible, setIsExtraConfigVisible] = useState(false);
   const { register, handleSubmit, errors, setValue, huggingFaceHealthCheck, loading, taskname } = useHuggingFace();

   const handleCheckboxChange = useCallback((e) => {
      setIsExtraConfigVisible(e.target.checked);
   }, []);

   const handleExtraConfigChange = useCallback((key, val) => {
      setExtraConfig((prev) => ({ ...prev, [key]: val }));
   }, []);

   const handleSwitchChange = useCallback((key, value) => {
      setSwitchConfig((prev) => ({ ...prev, [key]: value }));
    }, []);

   const submitHandler = async (data) => {
      const obj = {
         ...data,
         ...switchConfig,
         ...extraConfig
      }
      await huggingFaceHealthCheck(obj);
   }


   return (
      <>
         <div className="relative mb-4">
            <TooltipProvider>
               <Tooltip>
                     <TooltipTrigger>
                        <Label title={"Model Name"} htmlFor={"model-name"} />
                     </TooltipTrigger>
                     <TooltipContent className="border-none max-w-80">
                        <p className='text-font-14'>The specific identifier of the Hugging Face model you&apos;re using</p>
                     </TooltipContent>
               </Tooltip>
            </TooltipProvider>            
            <CommonInput
               placeholder='llama-3-2-3b-instruct-ctq'
               {...register('name')}
            />
            <ValidationError errors={errors} field={'name'}/>
         </div>
         <div className="relative mb-4">
            <TooltipProvider>
               <Tooltip>
                     <TooltipTrigger>
                        <Label title={"Task Type"} htmlFor={"TaskType"} />
                     </TooltipTrigger>
                     <TooltipContent className="border-none max-w-80">
                        <p className='text-font-14'>The specific application for which the model is designed, like text generation or sentiment analysis.</p>
                     </TooltipContent>
               </Tooltip>
            </TooltipProvider>
            <CommonSelectInput
               styles={customSelectStyles}
               options={TaskType}
               menuPlacement='auto'
               {...register('taskType')}
               onChange={(e) => {
                  setValue('taskType', e, { shouldValidate: true })
               }}
            />
            <ValidationError errors={errors} field={'taskType'}/>
         </div>
         <div className="relative mb-4">
            <TooltipProvider>
               <Tooltip>
                     <TooltipTrigger>
                        <Label title={"API Type"} htmlFor={"APIType"} />
                     </TooltipTrigger>
                     <TooltipContent className="border-none max-w-80">
                        <p className='text-font-14'>Choose the API service type, such as OpenAI or Claude via Bedrock, to align with your selected model or platform, ensuring seamless compatibility for handling text generation tasks.</p>
                     </TooltipContent>
               </Tooltip>
            </TooltipProvider>
            
            <CommonSelectInput
               options={APITypeOptions}
               isSearchable={false}
               {...register('apiType')}
               onChange={(e) => {
                  setValue('apiType', e, { shouldValidate: true })
               }}
            />
            <ValidationError errors={errors} field={'apiType'}/>
         </div>
         <div className="relative mb-4">
            <TooltipProvider>
               <Tooltip>
                     <TooltipTrigger>
                        <Label title={"Description"} htmlFor={"description"} required={false}/>
                     </TooltipTrigger>
                     <TooltipContent className="border-none max-w-80">
                        <p className='text-font-14'>{`A brief overview of the model's features and capabilities.`}</p>
                     </TooltipContent>
               </Tooltip>
            </TooltipProvider>
            
            <CommonInput
               className='default-form-input truncate'
               placeholder='Enter model description here'
               {...register('description')}
            />
            <ValidationError errors={errors} field={'description'}/>
         </div>
         <div className="relative mb-4">
            <TooltipProvider>
               <Tooltip>
                     <TooltipTrigger>
                        <Label title={"Model Endpoint URL"} htmlFor={"modelEndpointURL"} />
                     </TooltipTrigger>
                     <TooltipContent className="border-none max-w-80">
                        <p className='text-font-14'>{`The URL used to access the model's API endpoint for making requests.`}</p>
                     </TooltipContent>
               </Tooltip>
            </TooltipProvider>
            
            <CommonInput
               placeholder='https://huggingface.co/docs/inference-endpoints/en/guides/create_endpoint'
               {...register('endpoint')}
            />
            <ValidationError errors={errors} field={'endpoint'}/>
         </div>
         <div className="flex gap-5">
            <div className="relative mb-4 w-4/6">
               <TooltipProvider>
                  <Tooltip>
                        <TooltipTrigger>
                           <Label title={"Model Repository"} htmlFor={"ModelReposotory"} />
                        </TooltipTrigger>
                        <TooltipContent className="border-none max-w-80">
                           <p className='text-font-14'>The location where the model is hosted and maintained, typically on a platform like Hugging Face.</p>
                        </TooltipContent>
                  </Tooltip>
               </TooltipProvider>
               
               <CommonInput
                  placeholder='meta-llama/Llama-3.1-8B'
                  {...register('repo')}
               />
               <ValidationError errors={errors} field={'repo'}/>
            </div>
            {taskname?.code === taskCode.TEXT_GENERATION && (
               <div className="relative w-4/12">
                  <TooltipProvider>
                     <Tooltip>
                           <TooltipTrigger>
                           <Label title={"Context Length"} htmlFor={"ContextLength"} required={false} />
                           </TooltipTrigger>
                           <TooltipContent className="border-none max-w-80">
                              <p className='text-font-14'>The maximum number of tokens the model can process in a single input.</p>
                           </TooltipContent>
                     </Tooltip>
                  </TooltipProvider>
                  
                  <Slider
                  defaultValue={[extraConfig.value]}
                  min={8096}
                  max={12800}
                  step={1}
                  onValueChange={(val) => handleExtraConfigChange('value', val[0])}
               />
               <div className="text-font-14 font-bold mt-2">
                     {extraConfig.value}
                  </div>
               </div>
            )}
         </div>

         <HuggingFaceAPIInput register={register} errors={errors} configs={configs}/>
         {taskname?.code === taskCode.TEXT_GENERATION && (
            <>
               <div className="flex items-center space-x-2 mb-3">
                  <Switch id="Toolcall" checked={switchConfig.tool} onCheckedChange={(value) => handleSwitchChange('tool', value)} />
                  <div>
                     <Label className='mb-0 font-bold' required={false} title={"Tool Calls"} htmlFor={"Toolcall"} />
                     <span className='block text-font-12 text-b5'>{`Activate this if the model supports "functions" or "tool_calls."`}</span>
                  </div>
               </div>
               <hr className='mb-3 mt-3' />
            </>
         )}
         { taskname && (
            <div className="mb-5 block min-h-[1.5rem] ps-8">
               <CommonInput
                  className='input-checkbox'
                  type="checkbox"
                  id="extraConfig"
                  onChange={handleCheckboxChange}
            />
            <Label className='inline-block ps-[0.15rem] hover:cursor-pointer font-bold text-font-14' htmlFor='extraConfig' title={'Extra Configuration'} required={false} />
         </div> )}
         {isExtraConfigVisible && taskname?.code === taskCode.TEXT_GENERATION && (
            <div className="extra-config">
               <div className="flex gap-5">
                  <div className="relative mb-5 w-1/2">
                     <div className='flex justify-between items-center'>
                     <TooltipProvider>
                        <Tooltip>
                              <TooltipTrigger>
                                 <Label className='text-font-14 mb-2 font-bold block' title={"Temperature"} htmlFor={"temperature"} />
                              </TooltipTrigger>
                              <TooltipContent className="border-none max-w-80">
                                 <p className='text-font-14'>Controls randomness in responses; lower values yield more predictable results.</p>
                              </TooltipContent>
                        </Tooltip>
                     </TooltipProvider>
                        
                        <div className="text-font-14 font-bold mb-2">
                           {extraConfig.temperature}
                        </div>
                     </div>
                     <Slider
                        defaultValue={[extraConfig.temperature]}
                        min={0.0}
                        max={2.0}
                        step={0.1}
                        onValueChange={(val) => handleExtraConfigChange('temperature', val[0])}
                     />
                  </div>
                  <div className="relative mb-5 w-1/2">
                     <div className='flex justify-between items-center'>
                     <TooltipProvider>
                        <Tooltip>
                              <TooltipTrigger>
                              <Label className='text-font-14 mb-2 font-bold block' title={"Top K"} htmlFor={"topK"} />
                              </TooltipTrigger>
                              <TooltipContent className="border-none max-w-80">
                                 <p className='text-font-14'>Limits the model to the top K probable next words.</p>
                              </TooltipContent>
                        </Tooltip>
                     </TooltipProvider>
                        
                        <div className="text-font-14 font-bold mb-2">
                           {extraConfig.topK}
                        </div>
                     </div>
                     <Slider
                        defaultValue={[extraConfig.topK]}
                        min={1}
                        max={100}
                        step={1}
                        onValueChange={(val) => handleExtraConfigChange('topK', val[0])}
                     />
                  </div>
               </div>
               <div className="flex gap-5">
                  <div className="relative mb-5 w-1/2">
                     <div className='flex justify-between items-center'>
                     <TooltipProvider>
                        <Tooltip>
                              <TooltipTrigger>
                                 <Label className='text-font-14 mb-2 font-bold block' title={"Top P"} htmlFor={"topP"} />
                              </TooltipTrigger>
                              <TooltipContent className="border-none max-w-80">
                                 <p className='text-font-14'>Uses nucleus sampling to select from the top P percentage of words.</p>
                              </TooltipContent>
                        </Tooltip>
                     </TooltipProvider>
                        
                        <div className="text-font-14 font-bold mb-2">
                           {extraConfig.topP}
                        </div>
                     </div>
                     <Slider
                        defaultValue={[extraConfig.topP]}
                        min={0.0}
                        max={1.0}
                        step={0.05}
                        onValueChange={(val) => handleExtraConfigChange('topP', val[0])}
                     />
                  </div>
                  <div className="relative mb-5 w-1/2">
                     <div className='flex justify-between items-center'>
                     <TooltipProvider>
                        <Tooltip>
                              <TooltipTrigger>
                                 <Label className='text-font-14 mb-2 font-bold block' title={"Repetition Penalty"} htmlFor={"repetitionPenalty"} />
                              </TooltipTrigger>
                              <TooltipContent className="border-none max-w-80">
                                 <p className='text-font-14'>Penalizes repeated tokens to encourage diversity in output.</p>
                              </TooltipContent>
                        </Tooltip>
                     </TooltipProvider>
                        
                        <div className="text-font-14 font-bold mb-2">
                           {extraConfig.repetitionPenalty}
                        </div>
                     </div>
                     <Slider
                        defaultValue={[extraConfig.repetitionPenalty]}
                        min={0.0}
                        max={2.0}
                        step={0.01}
                        onValueChange={(val) => handleExtraConfigChange('repetitionPenalty', val[0])}
                     />
                  </div>
               </div>
               <div className='flex gap-5 items-center'>
                  <div className="relative mb-5 w-1/2">
                     <div className='flex justify-between items-center'>
                     <TooltipProvider>
                        <Tooltip>
                              <TooltipTrigger>
                              <Label className='text-font-14 mb-2 font-bold block' title={"Frequency Penalty"} htmlFor={"frequencyPenalty"} />
                              </TooltipTrigger>
                              <TooltipContent className="border-none max-w-80">
                                 <p className='text-font-14'>Reduces the likelihood of repeated phrases.</p>
                              </TooltipContent>
                        </Tooltip>
                     </TooltipProvider>                        
                        <div className="text-font-14 font-bold mb-2">
                           {extraConfig.frequencyPenalty}
                        </div>
                     </div>
                     <Slider
                        defaultValue={[extraConfig.frequencyPenalty]}
                        min={-2.0}
                        max={2.0}
                        step={1}
                        onValueChange={(val) => handleExtraConfigChange('frequencyPenalty', val[0])}
                     />
                  </div>
                  <div className="relative mb-5 w-1/2">
                     <div className='flex justify-between items-center'>
                     <TooltipProvider>
                        <Tooltip>
                              <TooltipTrigger>
                                 <Label className='text-font-14 mb-2 font-bold block' title={"Typical P"} htmlFor={"typicalP"} />
                              </TooltipTrigger>
                              <TooltipContent className="border-none max-w-80">
                                 <p className='text-font-14'>Adjusts sampling to favor more typical outputs.</p>
                              </TooltipContent>
                        </Tooltip>
                     </TooltipProvider>
                        
                        <div className="text-font-14 font-bold mb-2">
                           {extraConfig.typicalP}
                        </div>
                     </div>
                     <Slider
                        defaultValue={[extraConfig.typicalP]}
                        min={0.0}
                        max={1.0}
                        step={0.05}
                        onValueChange={(val) => handleExtraConfigChange('typicalP', val[0])}
                     />

                  </div>

               </div>

               <div className="flex gap-5 items-center">
                  <div className="relative mb-5 w-1/2">
                  <TooltipProvider>
                        <Tooltip>
                              <TooltipTrigger>
                                 <Label title={"Stop Sequences"} htmlFor={"stopSequences"} />
                              </TooltipTrigger>
                              <TooltipContent className="border-none max-w-80">
                                 <p className='text-font-14'>Defines sequences that, when generated, will stop the output.</p>
                              </TooltipContent>
                        </Tooltip>
                     </TooltipProvider>
                     
                     <CommonInput
                        {...register('sequences')}
                     />
                  </div>
                  <div className="relative w-1/2">
                     <Switch id="do-sample" checked={switchConfig.sample} onCheckedChange={(value) => handleSwitchChange('sample', value)}/>
                     <div>
                        <Label className='mb-0 font-bold text-font-14' required={false} title={"do-sample"} htmlFor={"do-sample"} />
                        <span className='block text-font-12 text-b5'>This parameter enables decoding</span>
                     </div>
                  </div>
               </div>

            </div>
         )}
         {
            isExtraConfigVisible && taskname?.code === taskCode.IMAGE_GENERATION && (
               <div className="flex gap-5">
                  <div className="relative mb-5 w-1/2">
                     <div className='flex justify-between items-center'>
                        <Label className='text-font-14 mb-2 font-bold block' title={'Num Inference'} />
                        <div className="text-font-14 font-bold mb-2">
                           {extraConfig.numInference}
                        </div>
                     </div>
                     <Slider
                        defaultValue={[extraConfig.numInference]}
                        min={5}
                        max={50}
                        step={1}
                        onValueChange={(val) => handleExtraConfigChange('numInference', val[0])}
                     />
                  </div>
                  <div className="relative mb-5 w-1/2">
                     <div className='flex justify-between items-center'>
                        <Label className='text-font-14 mb-2 font-bold block' title={'Guidance Scale'} />
                        <div className="text-font-14 font-bold mb-2">
                           {extraConfig.gScale}
                        </div>
                     </div>
                     <Slider
                        defaultValue={[extraConfig.gScale]}
                        min={1}
                        max={10}
                        step={1}
                        onValueChange={(val) => handleExtraConfigChange('gScale', val[0])}
                     />
                  </div>
               </div>
            )
         }
         <button 
            className="btn btn-black" 
            type="button"
            onClick={handleSubmit(submitHandler)}
             disabled={loading} 
         >
            Save
         </button>   
      </>
   );
};

export default memo(HuggingFaceModelProvider);