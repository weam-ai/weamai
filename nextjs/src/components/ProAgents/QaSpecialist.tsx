import { qaSpecialistSchema, QaSpecialistSchemaType } from '@/schema/proAgent';
import { ProAgentCode } from '@/types/common';
import CommonInput from '@/widgets/CommonInput';
import Label from '@/widgets/Label';
import ValidationError from '@/widgets/ValidationError';
import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form';
type QAProAgentProps = {
    setDialogOpen: (open: boolean) => void;
    handleSubmitPrompt: (proAgentData: { code: ProAgentCode, url: string }) => void;
}

const QAProAgent: React.FC<QAProAgentProps> = ({setDialogOpen, handleSubmitPrompt }) => {
    const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<QaSpecialistSchemaType>({
        resolver: yupResolver(qaSpecialistSchema),
        defaultValues: { url: '' },
        mode: 'onSubmit'
    });
    
    const onSubmit = (data: QaSpecialistSchemaType) => {
        handleSubmitPrompt({
            code: ProAgentCode.QA_SPECIALISTS,
            url: data.url,            
        });
        setDialogOpen(false);
    }
    return (
        <div className="qa-form">
            <div className="relative mb-4">
                <Label className="text-font-14 font-medium text-b2 mb-1 block" htmlFor="url" title="Website URL" />
                <CommonInput
                    placeholder="Enter the website URL to analyze (e.g., https://www.example.com)"
                    {...register('url')}
                />
                <ValidationError errors={errors} field='url' />
            </div>
            <div className="relative mb-4 flex gap-2">
                
                <button className="btn btn-outline-black text-font-14" disabled={isSubmitting} onClick={handleSubmit(onSubmit)}>
                    Run Agent
                </button>
            </div>
        </div>
    );
};

export default QAProAgent;

