import React from 'react';
import Label from '@/widgets/Label';
import Select from 'react-select'
import Image from 'next/image';
import AzureApiIcon from '../../../public/azure-API.svg'
import ApiKeyInput from './ApiKeyInput';

const AzureOpenAIModelProvider = () => {
    const selectModelYourDeploymentOptions = [
        { value: 'GPT-3.5 (Azure)', label: 'GPT-3.5 (Azure)' },
        { value: 'GPT-3.5-16k (Azure)', label: 'GPT-3.5-16k (Azure)' },
        { value: 'GPT-4 (Azure)', label: 'GPT-4 (Azure)' },
        { value: 'GPT-4-32k (Azure)', label: 'GPT-4-32k (Azure)' },
        { value: 'GPT-4-Turbo (Azure)', label: 'GPT-4-Turbo (Azure)' },
    ]
  return (
    <>
        <div className="relative mb-4">
            <Label title={"Azure OpenAI Endpoint"} htmlFor={"azureOpenAIEndpoint"}/>
            <input  type="text" className="default-form-input" id="azureOpenAIEndpoint" />
         </div>
         <div className="relative mb-4">
            <Label title={"Deployment Name"} htmlFor={"deploymentName"}/>
            <input  type="text" className="default-form-input" id="deploymentName" />
         </div>
         <div className="relative mb-4">
            <Label title={"API Version"} htmlFor={"APIVersion"}/>
            <input  type="text" className="default-form-input" id="APIVersion" />
         </div>
         <div className="relative mb-4">
            <Label title={"Select the model of your deployment"} htmlFor={"selectModelYourDeployment"}/>
            <Select options={selectModelYourDeploymentOptions} menuPlacement='auto' id="selectModelYourDeployment" className="react-select-container" classNamePrefix="react-select"/>
        </div>
        <ApiKeyInput labelName={"API key"} imgSrc={AzureApiIcon} imgAlt={"API key"} inputId={"azure-api-key"} labelhtmlFor={"azure-api-key"} className={"mb-4"}/>
    </>
  );
};

export default AzureOpenAIModelProvider;