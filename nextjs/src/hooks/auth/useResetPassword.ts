import { resetPasswordKeys } from '@/schema/auth';
import { yupResolver } from '@hookform/resolvers/yup';
import { useForm } from 'react-hook-form';
import { useSearchParams, useRouter } from 'next/navigation';
import commonApi from '@/api';
import { MODULES, MODULE_ACTIONS } from '@/utils/constant';
import Toast from '@/utils/toast';
import routes from '@/utils/routes';

const useResetPassword = () => {

    const router = useRouter()

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        resolver: yupResolver(resetPasswordKeys),
    });

    const searchParam = useSearchParams();
    const id = searchParam.get('id')
    const hash = searchParam.get('hash')
    
    const setPassword = async (payload) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.RESET_PASSWORD,
                module: MODULES.AUTH,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                data: { 
                    id,
                    password: payload.password,
                    resetHash: hash
                },
                common: true
            })
            Toast(response.message)
            router.push(routes.login)
        } catch (error) {
            console.log('error: ', error);
        }
    }

    return {
        register,
        handleSubmit,
        errors,
        setPassword
    }

};

export default useResetPassword