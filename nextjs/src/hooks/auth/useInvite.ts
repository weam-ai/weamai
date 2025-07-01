import commonApi from '@/api';
import { inviteUsersKeys } from '@/schema/auth';
import { MODULES, MODULE_ACTIONS } from '@/utils/constant';
import routes from '@/utils/routes';
import { yupResolver } from '@hookform/resolvers/yup';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useForm } from 'react-hook-form';

const useInvite = () => {
    const [isSend, setIsSend] = useState(false);
    const [loading, setLoading] = useState(false);
    const [userLimitExceed,setUserLimitExceed]=useState(0)


    const router = useRouter();

    const {
        register,
        handleSubmit,
        formState: { errors },
        setValue
    } = useForm({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        resolver: yupResolver(inviteUsersKeys)
    });

    const sendInvitation = async (users, role, home = false) => {
        setLoading(true);
        try {
        const data = {
            users: users.map(u => {
                return {
                    email: u.toLowerCase(),
                }
            }),
            roleCode: role.code
        }
        
        const dataAPI = await commonApi({
            action: MODULE_ACTIONS.INVITE_USER,
            prefix: MODULE_ACTIONS.ADMIN_PREFIX,
            module: MODULES.AUTH,
            common: true,
            data
        });

        if(dataAPI?.code=='SUCCESS'){
            setUserLimitExceed(dataAPI?.data?.userLimitExceed)
            setIsSend(true);
        }
        if (home) router.push(routes.main);
        } catch (error) {
            console.error(error);
        }    finally {
            setLoading(false);
        }
    };

    const handleFinish = () => {
        setIsSend(false);
    };

    return {
        register,
        handleSubmit,
        errors,
        sendInvitation,
        isSend,
        handleFinish,
        setValue,
        userLimitExceed,
        loading
    };
};

export default useInvite;
