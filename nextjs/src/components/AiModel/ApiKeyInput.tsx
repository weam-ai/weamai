import React from 'react';
import Image from 'next/image';
import { useDispatch, useSelector } from 'react-redux';
import {
    setAddTitle,
    setInputStatus,
    setVisibleAction,
} from '@/lib/slices/aimodel/aimodel';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { setModalAPIKeys } from '@/schema/usermodal';
import ValidationError from '@/widgets/ValidationError';
import commonApi from '@/api';
import { MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';
import { assignModelListAction } from '@/lib/slices/aimodel/assignmodelslice';
import { encryptedPersist } from '@/utils/helper';
import { CONFIG_API } from '@/utils/localstorage';
import { RootState } from '@/lib/store';

const ApiKeyInput = ({
    className,
    imgSrc,
    imgAlt,
    labelName,
    labelhtmlFor,
    inputId,
    apikey,
    setApiKeyUpdated,
    setShowCancelAPI      
}:any) => {
    const dispatch = useDispatch();
    const botinfo = useSelector((store:any) => store.aiModal.selectedValue);
    const assignmodalList = useSelector((store:any) => store.assignmodel.list);
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({
        mode: 'onSubmit',
        resolver: yupResolver(setModalAPIKeys),
    });
    const [loading, setLoading] = React.useState(false);

    const handleButtonClick = async (data) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.CHECK_API_KEY,
                data: {
                    key: data.key,
                    bot: {
                        title: botinfo.value,
                        code: botinfo.code,
                        id: botinfo.id,
                    },
                },
            });

            if(response.data && typeof response.data!="boolean"){
                const assignmodal = response?.data?.filter((el) => {
                    if(el.modelType!= SEARCH_AND_FILTER_OPTIONS.EMBEDDING_MODAL_TYPE)
                        return {
                            name: el.name,
                            bot: el.bot,
                            company: el.company,
                            config : { apikey: data.key } 
                        };
                });
                dispatch(
                    assignModelListAction([...assignmodal, ...assignmodalList])
                );
            }
            dispatch(setAddTitle(false));
            dispatch(setInputStatus(true));
            dispatch(setVisibleAction(false));
            setApiKeyUpdated(true);
            setShowCancelAPI(true)

            encryptedPersist(true,CONFIG_API)
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={`relative ${className}`}>
            <label
                htmlFor={labelhtmlFor}
                className="font-semibold mb-2 inline-block"
            >
                <span className="w-7 h-7 rounded-full bg-b11 inline-flex items-center justify-center me-2.5 align-middle">
                    <Image
                        src={imgSrc}
                        alt={imgAlt}
                        width={16}
                        height={16}
                        className="w-5 h-5 object-contain object-center inline-block"
                    />
                </span>
                {labelName}
            </label>
            <div className="gap-2.5 flex">
                <input
                    type="text"
                    className="default-form-input"
                    id={inputId}
                    {...register('key')}
                    defaultValue={apikey ? 'sk-xxxxxxxxxxxxxxxxxx' : ''}
                />
                
                    <button
                        className="btn btn-black"
                        type="button"
                        onClick={handleSubmit(handleButtonClick)}
                        disabled={loading}
                    >
                        Save
                    </button>            
                
            </div>
            <ValidationError errors={errors} field={'key'} />
        </div>
    );
};

export default ApiKeyInput;
