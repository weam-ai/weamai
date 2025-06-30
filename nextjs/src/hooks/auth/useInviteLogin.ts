import commonApi from '@/api';
import { MODULE_ACTIONS } from '@/utils/constant';
import { setUserData } from '@/utils/handleAuth';
import { encryptedPersist } from '@/utils/helper';
import { USER } from '@/utils/localstorage';
import Toast from '@/utils/toast';
import { useRouter, useSearchParams } from 'next/navigation';
import { useState } from 'react';
import { pushToMainChat, setLoginCookieData } from './useLogin';

const useInviteLogin = () => {
    const [loading, setLoading] = useState(false);
    const [linkExpire, setLinkExpire] = useState(false);
    const router = useRouter();
    const searchParam = useSearchParams();
    const token = searchParam.get('token');
    const hash = searchParam.get('hash');

    const inviteMemberLogin = async () => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.INVITE_LOGIN,
                data: {
                    inviteLink: `invite?token=${token}&hash=${hash}`,
                },
            });

            Toast(response.message);
            
            setLoginCookieData(response.data);
            const userInfo = setUserData(response.data)
            encryptedPersist(userInfo, USER);
            pushToMainChat(response, router);
        } catch (error) {
            setLinkExpire(true);
        } finally {
            setLoading(false);
        }
    };

    return {
        loading,
        inviteMemberLogin,
        linkExpire
    };
};

export default useInviteLogin;
