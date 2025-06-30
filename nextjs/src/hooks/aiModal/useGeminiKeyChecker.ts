import commonApi from '@/api';
import { assignModelListAction } from '@/lib/slices/aimodel/assignmodelslice';
import { MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';
import { encryptedPersist } from '@/utils/helper';
import { CONFIG_API } from '@/utils/localstorage';
import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { geminiKeys } from '@/schema/usermodal';
import Toast from '@/utils/toast';

const defaultValues:any = {
    key: undefined,
};

const useGeminiKeyChecker = () => {
    const [loading, setLoading] = useState(false);
    const botinfo = useSelector((store:any) => store.aiModal.selectedValue);
    const assignmodalList = useSelector((store:any) => store.assignmodel.list);
    const dispatch = useDispatch();

    const { register, handleSubmit, formState: { errors }, setValue } = useForm({
        mode: 'onSubmit',
        resolver: yupResolver(geminiKeys),
        defaultValues
    })

    const geminiKeyChecker = async (payload) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.CHECK_GEMINI_API_KEY,
                data: {
                    key: payload.key,
                    bot: {
                        title: botinfo.value,
                        code: botinfo.code,
                        id: botinfo.id,
                    }
                },
            });
            
            if (!response?.data?.modifiedCount) {
                dispatch(assignModelListAction([...assignmodalList, ...response.data]));
            }
            
            Toast(response.message);            
        } finally {
            setLoading(false);            
        }
    };

    return {
        geminiKeyChecker,
        loading,
        register,
        handleSubmit,
        errors,
        setValue
    }
};

export default useGeminiKeyChecker;