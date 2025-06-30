'use client';
import React, { useState, useEffect,useMemo, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import { companyDetailSchema, CompanyDetailSchemaType } from '@/schema/company';
import ValidationError from '@/widgets/ValidationError';
import Label from '@/widgets/Label';
import CommonInput from '@/widgets/CommonInput';
import Link from 'next/link';
import routes from '@/utils/routes';
import useCountry from '@/hooks/common/useCountry';
import Select from 'react-select';
import ReCAPTCHA from "react-google-recaptcha";
import { APP_ENVIRONMENT, RECAPTCHA } from '@/config/config';
import Script from "next/script"; 
import Toast from '@/utils/toast';
import useRecaptcha from '@/hooks/auth/useRecaptcha';
import { useRouter } from 'next/navigation';
import TagManager from 'react-gtm-module';

const BOT_CPS_THRESHOLD = 30; // Characters per second threshold for bot detection
import useServerAction from '@/hooks/common/useServerActions';
import { registerAction } from '@/actions/auth';
import { RESPONSE_STATUS } from '@/utils/constant';



const defaultValues = {
    firstName: undefined,
    lastName: undefined,
    companyNm: undefined,
    email: undefined,
    password: undefined,
    confirmPassword: undefined,
    country: null,
};

const CompanyDetails = () => {

    const {
        register,
        handleSubmit,
        formState: { errors },
        setValue,
        control
    } = useForm<CompanyDetailSchemaType>({
        mode: 'onSubmit',
        reValidateMode: 'onChange',
        defaultValues: defaultValues,
        resolver: yupResolver(companyDetailSchema),
    });
    const { countries } = useCountry();
    const { verifyCaptcha, showReCaptchaV2, captchaToken, setCaptchaToken } = useRecaptcha();
    const [useV2Captcha, setUseV2Captcha] = useState(true);

    const initialTypingMetrics = {
      firstName: { startTime: 0, charCount: 0, endTime: 0, isPotentiallyBot: false },
      lastName: { startTime: 0, charCount: 0, endTime: 0, isPotentiallyBot: false },
      companyNm: { startTime: 0, charCount: 0, endTime: 0, isPotentiallyBot: false },
      email: { startTime: 0, charCount: 0, endTime: 0, isPotentiallyBot: false },
    };
    const [typingMetrics, setTypingMetrics] = useState(initialTypingMetrics);
    const [registerCompany, loading] = useServerAction(registerAction);
    const router = useRouter();
    const countryOptions = useMemo(
      () =>
        (countries || []).map((country) => ({
          value: country.shortCode,
          label: country.nm,
        })),
      [countries]
    );

    const handleTypingStart = (fieldName: string) => {
      if (typingMetrics[fieldName].startTime === 0) {
        setTypingMetrics(prevMetrics => ({
          ...prevMetrics,
          [fieldName]: {
            ...prevMetrics[fieldName],
            startTime: Date.now(),
          }
        }));
      }
    };

    const handleTypingChange = (event: React.ChangeEvent<HTMLInputElement>, fieldName: string) => {
      const charCount = event.target.value.length;
      const startTime = typingMetrics[fieldName].startTime;
      const endTime = Date.now();

      if (startTime === 0) { 
        return;
      }

      const elapsedTimeInSeconds = (endTime - startTime) / 1000;
      let isPotentiallyBotForThisField = false;

      if (elapsedTimeInSeconds > 0.05 && charCount > 3) {
        const cps = charCount / elapsedTimeInSeconds;
        if (cps > BOT_CPS_THRESHOLD) {
          isPotentiallyBotForThisField = true;
        }
      }

      setTypingMetrics(prevMetrics => ({
        ...prevMetrics,
        [fieldName]: {
          ...prevMetrics[fieldName],
          charCount: charCount,
          endTime: endTime,
          isPotentiallyBot: prevMetrics[fieldName].isPotentiallyBot || isPotentiallyBotForThisField,
        }
      }));
    };

    const handleTypingEnd = (fieldName: string) => {
      setTypingMetrics(prevMetrics => ({
        ...prevMetrics,
        [fieldName]: {
          ...prevMetrics[fieldName], // Retains isPotentiallyBot
          startTime: 0,
          charCount: 0,
          endTime: 0,
        }
      }));
    };

     // Add this new function to prevent copy and paste
    const preventCopyPaste = (e: React.ClipboardEvent) => {
        e.preventDefault();
        Toast("Copy and paste functionality is disabled for security reasons", "error");
    };
    
    const recaptchaRef = useRef(null);

    const handleCaptchaChangeV2 = (token) => {
        setCaptchaToken(token);
        verifyCaptcha(token, "v2");
    };

    const handleCaptchaChangeV3 = (token) => {
        setCaptchaToken(token);
        verifyCaptcha(token, "v3");
    };

    /**
     * onSubmit is called by React Hook Form after successful validation.
     * We:
     *  1) Check if showReCaptchaV2 is true -> then user must solve v2.
     *  2) Otherwise (v3 path), we call grecaptcha.execute for a fresh token.
     *  3) If captcha is valid, call registerCompany with the form data.
     */
    const onSubmitWithCaptcha = async (formData) => {
        // Honeypot check
        const honeypotInput = document.getElementById('website_url_honeypot') as HTMLInputElement | null;
        if (honeypotInput && honeypotInput.value) {
            Toast("We detect you as a bot.", "error");
            return; 
        }

        // Typing speed bot check
        const monitoredFields = ['firstName', 'lastName', 'companyNm', 'email'];
        for (const fieldName of monitoredFields) {
            if (typingMetrics[fieldName].isPotentiallyBot) {
                Toast("We detect you as a bot.", "error");
                return;
            }
        }
        
        // Check if the environment is production and the email is present
        if (
            process.env.NEXT_PUBLIC_APP_ENVIRONMENT === 'production') {
            // Ensure the window object is available
            if (typeof window !== 'undefined') {
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                event: 'app_sign_up_form_submit',
                email: formData.email.toLowerCase(),
                first_name: formData.firstName,
                last_name: formData.lastName,
                country: formData.country ? formData.country.nm : null,
            });
            }
        }

        try {
            if (!captchaToken) {
                Toast("Please complete the reCAPTCHA verification first.", "error");
                return;
            }
           
            const response = await registerCompany(formData);
            if (response.status === RESPONSE_STATUS.CREATED) {
                Toast(response.message);
                router.push(routes.sendVerification);
            }
           else if ((window as any).grecaptcha) {
             
              (window as any).grecaptcha.ready(async () => {
                const token = await (window as any).grecaptcha.execute(RECAPTCHA.SITE_KEY_V3, {
                  action: 'submit',
                });
                setCaptchaToken(token);
    
                // Verify token with your server
                await verifyCaptcha(token, 'v3');
    
                if (showReCaptchaV2) {
                  Toast("Please complete the reCAPTCHA checkbox","error");
                  return;
                }

                const response = await registerCompany(formData);
                if (response.status === RESPONSE_STATUS.CREATED) {
                    Toast(response.message);
                    router.push(routes.sendVerification);
                }
              });
            }
            else {
             alert("reCAPTCHA is not loaded. Please refresh the page and try again.");
           }
        } catch (err) {
            console.error("Error on form submit:", err);
        }
    };

      useEffect(() => {
        if(APP_ENVIRONMENT === 'production'){
            const tagManagerArgs = {
                gtmId: 'GTM-WW8CBLMZ'
                };
                TagManager.initialize(tagManagerArgs);
            }

    }, []);

      
    return (   
        <>
            {/* Load reCAPTCHA v2 script */}
            <Script
                src={`https://www.google.com/recaptcha/api.js`}
                strategy="afterInteractive"
            />

            <form
                className="w-full max-w-[730px] mx-auto flex flex-wrap"
                onSubmit={handleSubmit(onSubmitWithCaptcha)}
                autoComplete="off" 
            >
                <div className="relative mb-4 w-full md:w-1/2 px-2">
                    <Label title={'First Name'} htmlFor={'FirstName'} className={'text-font-14 font-semibold inline-block mb-2.5 text-b2'}/>
                    <CommonInput
                            id={'FirstName'}
                            placeholder={'First Name'}
                            maxLength={30}
                            onCopy={preventCopyPaste}
                            onPaste={preventCopyPaste}
                            onCut={preventCopyPaste}
                            autoComplete="new-password" // Use non-standard value to trick browsers
                            autoFill="off"
                            onKeyDown={() => handleTypingStart('firstName')}
                            onChange={(e) => handleTypingChange(e, 'firstName')}
                            onBlur={() => handleTypingEnd('firstName')}
                            {...register('firstName')}
                    />
                    <ValidationError errors={errors} field={'firstName'} />
                </div>
                <div className="relative mb-4 w-full md:w-1/2 px-2">
                    <Label title={'Last Name'} htmlFor={'LastName'} className={'text-font-14 font-semibold inline-block mb-2.5 text-b2'}/>
                    <CommonInput
                            id={'LastName'}
                            placeholder={'Last Name'}
                            maxLength={30}
                            onCopy={preventCopyPaste}
                            onPaste={preventCopyPaste}
                            onCut={preventCopyPaste}
                            autoComplete="new-password" // Use non-standard value to trick browsers
                            autoFill="off"
                            onKeyDown={() => handleTypingStart('lastName')}
                            onChange={(e) => handleTypingChange(e, 'lastName')}
                            onBlur={() => handleTypingEnd('lastName')}
                            {...register('lastName')}
                    />
                    <ValidationError errors={errors} field={'lastName'} />
                </div>
                <div className="relative mb-4 w-full md:w-1/2 px-2">
                    <Label title={'Company Name'} htmlFor={'CompanyName'} className={'text-font-14 font-semibold inline-block mb-2.5 text-b2'}/>
                    <CommonInput
                        id={'CompanyName'}
                        placeholder={'Advance Care Inc.'}
                        onCopy={preventCopyPaste}
                        onPaste={preventCopyPaste}
                        onCut={preventCopyPaste}
                        autoComplete="new-password" // Use non-standard value to trick browsers
                        autoFill="off"
                        onKeyDown={() => handleTypingStart('companyNm')}
                        onChange={(e) => handleTypingChange(e, 'companyNm')}
                        onBlur={() => handleTypingEnd('companyNm')}
                        {...register('companyNm')}
                        maxLength={50}
                    />
                    <ValidationError errors={errors} field={'companyNm'} />
                </div>
                <div className="relative mb-4 w-full md:w-1/2 px-2">
                    <Label title={'Email address'} htmlFor={'email'} className={'text-font-14 font-semibold inline-block mb-2.5 text-b2'}/>
                    <CommonInput
                        type={'email'}
                        id={'email'}
                        placeholder={'example@company.com'}
                        onCopy={preventCopyPaste}
                        onPaste={preventCopyPaste}
                        onCut={preventCopyPaste}
                        autoComplete="new-password" // Use non-standard value to trick browsers
                        autoFill="off"
                        onKeyDown={() => handleTypingStart('email')}
                        {...register('email')}
                        maxLength={320}
                        onChange={(e) => {
                            setValue('email', e.target.value.toLowerCase());
                            handleTypingChange(e, 'email');
                        }}
                        onBlur={() => handleTypingEnd('email')}
                    />
                    <ValidationError errors={errors} field={'email'} />
                </div>
                <div className="relative mb-4 w-full md:w-1/2 px-2">
                    <Label title={'Password'} htmlFor={'password'} className={'text-font-14 font-semibold inline-block mb-2.5 text-b2'} />
                    <CommonInput
                        id={'password'}
                        type={'password'}
                        placeholder={'Type your password'}
                        onCopy={preventCopyPaste}
                        onPaste={preventCopyPaste}
                        onCut={preventCopyPaste}
                        autoComplete="new-password" // Use non-standard value to trick browsers
                        autoFill="off"
                        {...register('password')}
                        maxLength={30}
                    />
                    <ValidationError errors={errors} field={'password'} />
                </div>
                <div className="relative mb-4 w-full md:w-1/2 px-2">
                    <Label title={'Confirm Password'} htmlFor={'ConfirmPassword'} className={'text-font-14 font-semibold inline-block mb-2.5 text-b2'} />
                    <CommonInput
                        id={'ConfirmPassword'}
                        type={'password'}
                        placeholder={'Confirm Password'}
                        onCopy={preventCopyPaste}
                        onPaste={preventCopyPaste}
                        onCut={preventCopyPaste}
                        autoComplete="new-password" // Use non-standard value to trick browsers
                        autoFill="off"
                        {...register('confirmPassword')}
                        maxLength={30}
                    />
                    <ValidationError
                        errors={errors}
                        field={'confirmPassword'}
                    />
                </div>
                <div className="relative mb-4 w-full md:w-1/2 px-2">
                    <Label 
                        title={'Country'} 
                        htmlFor={'country'} 
                        className={'text-font-14 font-semibold inline-block mb-2.5 text-b2'}
                    />
                    <Select
                        id="country"
                        options={countryOptions}
                        placeholder="Select Country"
                        className="react-select-container"
                        classNamePrefix="react-select"
                        onChange={(option:any) => setValue('country', option ? { 
                            shortCode: option.value,
                            nm: option.label 
                        } : null, { shouldValidate: true } )}
                        isClearable
                        isSearchable
                        styles={{
                            control: (baseStyles, state) => ({
                                ...baseStyles,
                                minHeight: '46px',
                                borderColor: state.isFocused ? '#blue' : '#E5E7EB',
                                '&:hover': {
                                    borderColor: '#blue'
                                }
                            }),
                        }}
                    />
                    <ValidationError errors={errors} field={'country'} />
                </div>

                {/* Honeypot field */}
                <div style={{ position: 'absolute', left: '-9999px', top: '-9999px' }}>
                  <label htmlFor="website_url_honeypot">Do not fill this out</label>
                  <input type="text" id="website_url_honeypot" name="website_url" autoComplete="off" tabIndex={-1} />
                </div>

                {/* Visible reCAPTCHA with image challenges */}
                <div className="w-full flex justify-center my-4">
                    <ReCAPTCHA
                        ref={recaptchaRef}
                        sitekey={RECAPTCHA.SITE_KEY_V2}
                        onChange={handleCaptchaChangeV2}
                        size="normal"
                        theme="light"
                        badge="bottomright"
                        onExpired={() => setCaptchaToken('')}
                        onError={() => {
                            Toast("Error loading reCAPTCHA. Please refresh the page.", "error");
                            setCaptchaToken('');
                        }}
                    />
                </div>
                
                <div className="submit-wrap flex items-center justify-center mt-2 md:mt-10 mx-auto w-full">
                    <button className="btn btn-blue py-[12px] w-full max-w-[300px]" disabled={loading}>
                        Sign Up
                    </button>
                </div>
                <p className="mb-5 mt-3 md:mb-0 mx-auto w-full text-center text-b7">
                Already have an account? <Link className='text-blue hover:text-black font-bold' href={routes.login}>Sign In</Link>
                </p>
            </form>
            </>
    );
};

export default CompanyDetails;
