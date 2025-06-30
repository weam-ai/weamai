import commonApi from '@/api';
import { assignModelListAction } from '@/lib/slices/aimodel/assignmodelslice';
import { anthropicKeys } from '@/schema/usermodal'
import { MODULE_ACTIONS } from '@/utils/constant';
import Toast from '@/utils/toast';
import { yupResolver } from '@hookform/resolvers/yup'
import { useState } from 'react';
import { useForm } from 'react-hook-form'
import { useSelector, useDispatch } from 'react-redux';

const defaultValues:any = {
    key: undefined,
};

const useAnthropic = () => {
    const { register, handleSubmit, formState: { errors }, setValue } = useForm({
        mode: 'onSubmit',
        resolver: yupResolver(anthropicKeys),
        defaultValues
    })
    const [loading, setLoading] = useState(false);
    const botinfo = useSelector((store:any) => store.aiModal.selectedValue);
    const assignmodalList = useSelector((store:any) => store.assignmodel.list);
    const dispatch = useDispatch();

    const anthropicHealthCheck = async (payload) => {
        try {
            setLoading(true);
            const data = {
                key: payload?.key,
                bot: {
                    title: botinfo.value,
                    code: botinfo.code,
                    id: botinfo.id,
                },
            }
            const response = await commonApi({
                action: MODULE_ACTIONS.ANTHROPIC_HEALTH,
                data
            })
            
            Toast(response.message);
            if (response.data === true) return;
            else dispatch(assignModelListAction([...assignmodalList, ...response.data]))
        } finally {
            setLoading(false);
        }
    }

    return {
        register,
        handleSubmit,
        errors,
        setValue,
        anthropicHealthCheck,
        loading,
    } 
}

export default useAnthropic;