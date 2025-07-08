import React from 'react';
import AnthropicAPIKeyIcon from '../../../public/Anthropic-API-Key.svg';
import Image from 'next/image';
import CommonInput from '@/widgets/CommonInput';
import useAnthropic from '@/hooks/aiModal/useAnthropic';
import ValidationError from '@/widgets/ValidationError';
import { useSelector } from 'react-redux';
import { RootState } from '@/lib/store';
const AnthropicModelProvider = ({ configs }) => {
    const { register, handleSubmit, anthropicHealthCheck, loading, errors } = useAnthropic();
    return (
        <div className={`relative mb-4`}>
            <label className="font-semibold mb-2 inline-block">
                <span className="w-7 h-7 rounded-full bg-b11 inline-flex items-center justify-center me-2.5 align-middle">
                    <Image
                        src={AnthropicAPIKeyIcon}
                        alt={'Anthropic'}
                        width={16}
                        height={16}
                        className="w-5 h-5 object-contain object-center inline-block"
                    />
                </span>
                {`Input Your Anthropic API Key`}
            </label>
            <div className="gap-2.5 flex">
                <CommonInput 
                    {...register('key')}
                    placeholder={'sk-ant-xxxxxxxxxxxxxxxxxx'}
                    defaultValue={configs?.apikey ? 'sk-ant-xxxxxxxxxxxxxxxxxx' : ''}
                />
                <button className="btn btn-black" type="button" disabled={loading} onClick={handleSubmit(anthropicHealthCheck)}>
                    Save
                </button>
            </div>
            <ValidationError errors={errors} field={'key'}/>
        </div>
    );
};

export default AnthropicModelProvider;
