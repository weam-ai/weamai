import commonApi from '@/api';
import { setProfileImgAction } from '@/lib/slices/profile/profileSlice';
import { MODULE_ACTIONS, MODULES } from '@/utils/constant';
import { setUserData } from '@/utils/handleAuth';
import { encryptedPersist } from '@/utils/helper';
import { USER } from '@/utils/localstorage';
import routes from '@/utils/routes';
import Toast from '@/utils/toast';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { useDispatch } from 'react-redux';

const useProfile = () => {
    const [loading, setLoading] = useState(false);
    const [profileInfo, setProfileInfo] = useState();
    const dispatch = useDispatch();
    const router = useRouter();

    const getProfile = async(id) => {
        try{
            const response = await commonApi({
                action: MODULE_ACTIONS.GET_PROFILE,
                parameters: [id]               
            })

            setProfileInfo(response.data);

        } catch (error) {
            console.log('error: ', error);
        }
    }

    const updateProfile = async (payload, id) => { 
        try {
            setLoading(true); 
            const response = await commonApi({
                parameters: [id],
                action: MODULE_ACTIONS.UPDATE_PROFILE,
                data: payload                
            })
            Toast(response.message); 
            const userInfo = setUserData(response.data);
            dispatch(setProfileImgAction(userInfo?.profileImg));
            encryptedPersist(userInfo, USER);
            router.push(routes.main);            
        } finally {
            setLoading(false)
        }
    } 

    const changePassword = async (payload, reset) => { 
        try {
            setLoading(true); 
            const response = await commonApi({
                action: MODULE_ACTIONS.CHANGE_PASSWORD,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.AUTH,
                data: {
                    newpassword: payload.password,
                    oldpassword: payload.oldpassword
                },
                common: true                
            })
            Toast(response.message);          
        } finally {
            setLoading(false)
            reset();
        }
    } 

    return {
        getProfile,
        profileInfo,
        updateProfile,
        setProfileInfo,
        loading,
        changePassword
    }
}

export default useProfile;