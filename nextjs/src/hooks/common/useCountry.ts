import { MODULE_ACTIONS, MODULES } from '@/utils/constant';
import { useState, useEffect } from 'react';
import commonApi from '@/api';
import { useSelector } from 'react-redux';
import { useDispatch } from 'react-redux';
import { cacheCountry } from '@/lib/slices/auth/signupDetails';
import { getCountryListAction } from '@/actions/common';
import { CountriesType } from '@/types/common';

const useCountry = () => {
    const [countries, setCountries] = useState([]);
    const cache = useSelector((store:any) => store.signup.countryList);
    const dispatch = useDispatch();

    const getCountries = async () => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                module: MODULES.COUNTRY,
                prefix: MODULE_ACTIONS.COMMON_PREFIX,
                data: {
                    options: {
                        pagination: false,
                        sort:{
                            nm: 1
                        }
                    }
                },
                common: true,
            });
            setCountries(response.data);
            dispatch(cacheCountry(response.data))
        } catch (error) {
            console.log('error: ', error);
        }
    };

    useEffect(() => {
        if (cache.length) {
            setCountries(cache)
        } else {
            getCountries();
        }
    }, [])
    

    return { countries };
};

export default useCountry;
