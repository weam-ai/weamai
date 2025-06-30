'use client';
import React from 'react';
import TwoFactorIcon from '@/icons/TwoFactorIcon';
import AuthFooter from '@/components/Auth/AuthFooter';
import BackButton from '@/widgets/BackButton';
import routes from '@/utils/routes';
import LoginMfaForm from '@/components/Auth/Login/LoginMfa';

export default function TwoFactorAuthForm() {
    return (
        <>
            <div className="flex flex-col h-full w-full">
                <div className="flex flex-nowrap h-full">
                    <div className="px-[30px] pt-[30px] flex flex-col w-full">
                        <BackButton href={routes.login} />
                        <div className="forgot-password-form flex flex-col flex-1 items-center justify-center w-full max-w-[500px] mx-auto">
                            <TwoFactorIcon
                                width={60}
                                height={60}
                                className="w-[60px] h-[60px] object-contain mb-5"
                            />
                            <h2 className="text-[26px] sm:text-[30px] font-semibold leading-normal mb-10 text-b2">
                                Two-factor Authentication
                            </h2>
                            <p className="text-center text-font-16 text-b5 max-w-[450px] mx-auto">
                                Open the app on your mobile device that you used
                                when setting up two-factor (such as Authy or
                                Authenticator) and enter the 6-digit code it
                                generates.
                            </p>
                            <LoginMfaForm />
                        </div>
                        <AuthFooter />
                    </div>
                </div>
            </div>
        </>
    );
}
