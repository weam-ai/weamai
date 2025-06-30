import useProAgent from '@/hooks/conversation/useProAgent';
import { seoTopicGenerationSchema, SeoTopicGenerationSchemaType } from '@/schema/proAgent';
import CommonInput from '@/widgets/CommonInput';
import Label from '@/widgets/Label';
import ValidationError from '@/widgets/ValidationError';
import { yupResolver } from '@hookform/resolvers/yup';
import React from 'react';
import { useForm } from 'react-hook-form';
import { SeoArticleGenerationLoader } from '../Loader/SeoArticleGenerationLoader';

const defaultValues = {
    topic: undefined
}

type SeoTopicGenerationProps = {
    messageId: string;
    keywords: string[];
    topicName: string;
    socket: any;
    generateSeoArticle: any;
    loading: boolean;
    primaryKeyword: string;
}

const SeoTopicGeneration = ({ messageId, keywords, topicName, socket, generateSeoArticle, loading, primaryKeyword }: SeoTopicGenerationProps) => {
    const { register, handleSubmit, formState: { errors }, setValue } = useForm<SeoTopicGenerationSchemaType>({
        mode: 'onSubmit',
        resolver: yupResolver(seoTopicGenerationSchema),
        defaultValues
    });
    const { generateSeoTopicName, isLoading } = useProAgent();

    const onSubmit = async (data: SeoTopicGenerationSchemaType) => {
        const response = await generateSeoArticle({ 
            messageId, 
            topicName: data.topic 
        }, socket);
        
    }

    const handleRegenerate = async() => {
        const response = await generateSeoTopicName({ messageId, secondaryKeywords: keywords, primaryKeyword });
        if (response) {
            setValue('topic', response.data.topics);
        }
    }

    return (
        <div className="topic">
            {
                loading ? <SeoArticleGenerationLoader loading={loading} /> :
                <>
                    <p className="text-font-16 font-medium mb-2">Generate SEO Topic</p>
                    <p className="text-font-14 mb-3">
                        <strong>Targeted Keywords: </strong>
                        {keywords.join(', ')}
                    </p>
                    <Label title={'Topic'} htmlFor={'topic'} />
                    <CommonInput
                        type="text"
                        className="default-form-input"
                        id="topic"
                        {...register('topic')}
                        defaultValue={topicName}
                    />
                    <ValidationError errors={errors} field={'topic'} />
                    <div className="flex justify-center gap-3 mt-5">
                        <button className="btn btn-outline-black" disabled={isLoading || loading} onClick={handleRegenerate}>Regenerate</button>
                        <button className="btn btn-black" disabled={isLoading || loading} onClick={handleSubmit(onSubmit)}>Generate Article</button>
                    </div>
                </>
            }
        </div>
    );
};

export default SeoTopicGeneration;
