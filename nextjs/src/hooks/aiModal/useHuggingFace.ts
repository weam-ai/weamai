import commonApi from '@/api';
import { assignModelListAction } from '@/lib/slices/aimodel/assignmodelslice';
import { huggingFaceKeys } from '@/schema/usermodal'
import { MODULE_ACTIONS } from '@/utils/constant';
import Toast from '@/utils/toast';
import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react';
import { useForm } from 'react-hook-form'
import { useSelector, useDispatch } from 'react-redux';

const defaultValues:any = {
    name: undefined,
    taskType: undefined,
    apiType: undefined,
    description: undefined,
    endpoint: undefined,
    repo: undefined,
    sequences: undefined,
    key: undefined
};

const useHuggingFace = () => {
    const { register, handleSubmit, formState: { errors }, setValue, getValues } = useForm({
        mode: 'onSubmit',
        resolver: yupResolver(huggingFaceKeys),
        defaultValues
    })
    const [loading, setLoading] = useState(false);
    const botinfo = useSelector((store:any) => store.aiModal.selectedValue);
    const assignmodalList = useSelector((store:any) => store.assignmodel.list);
    const dispatch = useDispatch();
    const taskname = getValues('taskType');

    const huggingFaceHealthCheck = async (payload) => {
        try {
            setLoading(true);
            const data = {
                name: payload?.name,
                taskType: payload?.taskType?.code,
                apiType: payload?.apiType?.value,
                description: payload?.description,
                endpoint: payload?.endpoint,
                repo: payload?.repo,
                tool: payload?.tool,
                sample: payload?.sample,
                context: payload?.value,
                frequencyPenalty: payload?.frequencyPenalty,
                topK: payload?.topK,
                topP: payload?.topP,
                typicalP: payload?.typicalP,
                repetitionPenalty: payload?.repetitionPenalty,
                temperature: payload?.temperature,
                sequences: payload?.sequences,
                key: payload?.key,
                bot: {
                    title: botinfo.value,
                    code: botinfo.code,
                    id: botinfo.id,
                },
                numInference: payload.numInference,
                gScale: payload.gScale,
            }
            const response = await commonApi({
                action: MODULE_ACTIONS.HUGGING_FACE_HEALTH,
                data
            })
            // handle config update case 
            Toast(response.message);
            if (response.data === true) return;
            else dispatch(assignModelListAction([...assignmodalList, response.data]))
        } finally {
            setLoading(false);
        }
    }

    return {
        register,
        handleSubmit,
        errors,
        setValue,
        huggingFaceHealthCheck,
        loading,
        taskname
    } 
}

export default useHuggingFace