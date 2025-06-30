import React from 'react';
import AiIcon from '../../../public/Ai-icon.svg';
import ApiKeyInput from './ApiKeyInput';

const OpenAiAPIKeysModelProvider = ({configs, setApiKeyUpdated,setShowCancelAPI }) => {
    return (
        <ApiKeyInput
            labelName={'Open AI API key'}
            imgSrc={AiIcon}
            imgAlt={'Open AI API key'}
            inputId={'open-ai-api-key'}
            labelhtmlFor={'open-ai-api-key'}
            className={'mb-4'}
            apikey={configs?.apikey}
            setApiKeyUpdated={setApiKeyUpdated}
            setShowCancelAPI={setShowCancelAPI}
        />
    );
};

export default OpenAiAPIKeysModelProvider;
