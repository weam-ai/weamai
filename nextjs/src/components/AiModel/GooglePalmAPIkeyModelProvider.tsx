import React from 'react';
import GeminiIcon from '../../../public/gemini_1_5_flash.png'
import Image from 'next/image';
import CommonInput from '@/widgets/CommonInput';
import useGeminiKeyChecker from '@/hooks/aiModal/useGeminiKeyChecker';
import ValidationError from '@/widgets/ValidationError';
const GooglePalmAPIkeyModelProvider = ({ configs }) => {
    const { register, handleSubmit, loading, geminiKeyChecker, errors } = useGeminiKeyChecker();
    return (
        <div className={`relative mb-4`}>
            <label className="font-semibold mb-2 inline-block">
                <span className="w-7 h-7 rounded-full bg-b11 inline-flex items-center justify-center me-2.5 align-middle">
                    <Image
                        src={GeminiIcon}
                        alt={'Gemini'}
                        width={16}
                        height={16}
                        className="w-5 h-5 object-contain object-center inline-block"
                    />
                </span>
                {`Gemini API key`}
            </label>
            <div className="gap-2.5 flex">
                <CommonInput 
                    {...register('key')}
                    placeholder={'xxxxxxxxxxxxxxxxxxxx'}
                    defaultValue={configs?.apikey ? 'xxxxxxxxxxxxxxxxxxxx' : ''}
                />
                <button className="btn btn-black" type="button" disabled={loading} onClick={handleSubmit(geminiKeyChecker)}>
                    Save
                </button>
            </div>
            <ValidationError errors={errors} field={'key'}/>
        </div>
    );
};

export default GooglePalmAPIkeyModelProvider;
