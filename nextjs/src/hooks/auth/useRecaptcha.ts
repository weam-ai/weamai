// useRecaptcha.js
import { useState } from 'react';

function useRecaptcha() {
  const [captchaToken, setCaptchaToken] = useState('');
  const [captchaScore, setCaptchaScore] = useState(null);
  const [showReCaptchaV2, setShowReCaptchaV2] = useState(false);

  const verifyCaptcha = async (token, version) => {
    try {
      const response = await fetch('/api/verifyCaptcha', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, version }),
      });

      const data = await response.json();
      if (data.success) {
        if (version === 'v3') {
          setCaptchaScore(data.score);
          if (data.score < 0.5) {
            setShowReCaptchaV2(true);
          }
        }
      } else {
        console.error('reCAPTCHA verification failed:', data.message);
      }
    } catch (error) {
      console.error('Error verifying captcha:', error);
    }
  };

  return {
    captchaToken,
    setCaptchaToken,
    captchaScore,
    showReCaptchaV2,
    setShowReCaptchaV2,
    verifyCaptcha,
  };
}

export default useRecaptcha;
