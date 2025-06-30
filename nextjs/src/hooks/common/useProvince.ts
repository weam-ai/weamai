import { MODULE_ACTIONS, MODULES } from '@/utils/constant';
import { useState } from 'react';
import commonApi from '@/api';
import { useDispatch } from 'react-redux';
import { cacheState } from '@/lib/slices/auth/signupDetails';

const useProvince = ({ cntry }) => {
    const [states, setStates] = useState([]);
    const dispatch = useDispatch();

    const getStates = async () => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                module: MODULES.STATE,
                prefix: MODULE_ACTIONS.COMMON_PREFIX,
                data: {
                    options: {
                        pagination: false
                    },
                    query: {
                        'country.code': cntry.code
                    }
                },
                common: true,
            });
            setStates(response.data);
            dispatch(cacheState(response.data));
        } catch (error) {
            console.log('error: ', error);
        }
    };

    return { states, getStates, setStates };
};

export default useProvince;
