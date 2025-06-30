import React from 'react';
import Label from '@/widgets/Label';
import Select from 'react-select'
import AnyscaleApiIcon from '../../../public/Anyscale-logo.svg'
import ApiKeyInput from './ApiKeyInput';

const AnyscaleModelProvider = () => {
    const selectModelYourDeploymentOptions = [
        { value: 'Llama 2 7B Chat HF', label: 'Llama 2 7B Chat HF' },
        { value: 'CodeLLama 34B Instruct HF', label: 'CodeLLama 34B Instruct HF' },
        { value: 'Llama 2 7B Chat HF', label: 'Llama 2 7B Chat HF' },
        { value: 'Llama 2 13B Chat HF', label: 'Llama 2 13B Chat HF' },
        { value: 'Llama 2 70B Chat HF', label: 'Llama 2 70B Chat HF' },
        { value: 'Mistral 7B', label: 'Mistral 7B' },
        { value: 'Mistral 7B InNSTRUCT v0.1', label: 'Mistral 7B InNSTRUCT v0.1' },
        { value: 'Zephyr 7B BETA', label: 'Zephyr 7B BETA' }
    ]
  return (
    <>
        <div className="relative mb-4">
            <Label title={"Anyscale Engpoint"} htmlFor={"Anyscale Engpoint"}/>
            <input  type="text" className="default-form-input" id="anyscaleEngpoint" />
         </div>
         <div className="relative mb-4">
            <Label title={"Select Default Model"} htmlFor={"selectDefaultModel"}/>
            <Select options={selectModelYourDeploymentOptions} menuPlacement='auto' id="selectDefaultModel" className="react-select-container" classNamePrefix="react-select"/>
        </div>
        <ApiKeyInput labelName={"API key"} imgSrc={AnyscaleApiIcon} imgAlt={"Anyscale API key"} inputId={"anyscale-api-key"} labelhtmlFor={"anyscale-api-key"} className={"mb-4"}/>
    </>
  );
};

export default AnyscaleModelProvider;