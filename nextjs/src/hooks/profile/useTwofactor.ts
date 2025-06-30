import commonApi from '@/api';
import { MODULE_ACTIONS } from '@/utils/constant';
import { getCurrentUser } from '@/utils/handleAuth';
import { encryptedPersist } from '@/utils/helper';
import { USER } from '@/utils/localstorage';
import Toast from '@/utils/toast';
import { useState } from 'react';

const useTwofactor = () => {
    
    const userDetail = getCurrentUser();
    const [QrCode, setQrCode] = useState('');
    const [twomfa, setTwomfa] = useState(userDetail?.mfa);

    const generateMfaSecret = async(payload) => {
        try{
            const response = await commonApi({
                action: MODULE_ACTIONS.GENERATE_MFA_SECRET,
                data: payload
            });

            if(response?.status == 200){
                setQrCode(response?.data?.qrData);
            }    
        } catch (error) {
            console.log('error: ', error);
        }
    }

    const mfaVerification = async(payload, userData) => {
        try{
            const response = await commonApi({
                action: MODULE_ACTIONS.MFA_VERIFICATION,
                data: payload
            });
            Toast(response.message); 
            
            if(response?.status == 200){
                userData.mfa = true;
                setTwomfa(true); 
                encryptedPersist(userData, USER);
            }
        } catch (error) {
            console.log('error: ', error);
        }
    }

    return {
        generateMfaSecret,
        QrCode,
        mfaVerification,
        setTwomfa,
        twomfa
    }
}

export default useTwofactor;