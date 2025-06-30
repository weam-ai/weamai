import React from 'react';
import Image from 'next/image';
import ChangePasswordIcon from '../../../../public/forgot-password.svg';
import AuthFooter from '@/components/Auth/AuthFooter';
import dynamic from 'next/dynamic';

// Dynamically import the ResetPasswordForm to avoid issues with SSR
const ResetPasswordForm = dynamic(
    () => import('@/components/Auth/ResetPassword/ResetPassword'),
    {
        ssr: false,
    }
);

export default function ForgotPassword() {
    return (
        <>
            <div className="flex flex-col h-full w-full">
                <div className="flex flex-nowrap h-full">
                    <div className="px-[30px] pt-[30px] flex flex-col w-full">
                        <div className="forgot-password-form flex flex-col flex-1 items-center justify-center w-full max-w-[500px] mx-auto">
                            <Image
                                src={ChangePasswordIcon}
                                width={60}
                                height={60}
                                className="w-[50px] sm:w-[60px] object-contain mb-5"
                                alt="Reset Password"
                            />
                            <h2 className="text-[26px] sm:text-[30px] font-semibold leading-normal mb-10 text-b2">
                                Create New Password
                            </h2>
                            <ResetPasswordForm />
                        </div>
                        <AuthFooter />
                    </div>
                </div>
            </div>
        </>
    );
}
