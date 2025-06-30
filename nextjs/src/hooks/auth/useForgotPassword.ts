import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { MODULE_ACTIONS, MODULES } from '@/utils/constant';
import Toast from '@/utils/toast';
import { forgotPasswordKeys } from '@/schema/auth';
import commonApi from '@/api';

const defaultValues:any = {
    email: undefined
}

const useForgotPassword = () => {
   
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        defaultValues: defaultValues,
        resolver: yupResolver(forgotPasswordKeys),
    });

    const forgotPassword = async (email, setShowMessage) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.FORGOT_PASSWORD,
                module: MODULES.AUTH,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                common: true,
                data: { email },
            });
            Toast(response.message);
            setShowMessage(true)
        } catch (error) {
            console.log('error: ', error);
        }
    };

    return {
        register,
        handleSubmit,
        errors,
        forgotPassword,
    };
};

export default useForgotPassword