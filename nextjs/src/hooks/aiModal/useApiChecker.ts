import commonApi from '@/api';
import { assignModelListAction } from '@/lib/slices/aimodel/assignmodelslice';
import { MODULE_ACTIONS, SEARCH_AND_FILTER_OPTIONS } from '@/utils/constant';
import { encryptedPersist } from '@/utils/helper';
import { CONFIG_API } from '@/utils/localstorage';
import { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';

const useApiChecker = () => {
    const [loading, setLoading] = useState(false);
    const [billingError, setBillingError] = useState(false);
    const assignmodalList = useSelector((store:any) => store.assignmodel.list);
    const dispatch = useDispatch();
    const openAIKeyChecker = async (data) => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.CHECK_API_KEY,
                data: {
                    key: data.key,
                    bot: data.bot,
                },
            });
    
            if (response.data && typeof response.data != 'boolean') {
                const assignmodal = response?.data?.filter((el) => {
                    if (el.modelType != SEARCH_AND_FILTER_OPTIONS.EMBEDDING_MODAL_TYPE)
                        return {
                            name: el.name,
                            bot: el.bot,
                            company: el.company,
                            config: { apikey: data.key },
                        };
                });
                dispatch(assignModelListAction([...assignmodal, ...assignmodalList]));
                encryptedPersist(true, CONFIG_API);
            }
    
        } finally {
            setLoading(false);
            if (!assignmodalList.length) setBillingError(true);
        }
    };

    return {
        openAIKeyChecker,
        loading,
        billingError,
        setBillingError
    }
};

export default useApiChecker;
