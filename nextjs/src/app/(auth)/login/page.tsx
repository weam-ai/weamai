import React from 'react';
import Image from 'next/image';
import LoginIcon from '@/../public/login-icon.svg';
import LoginForm from '@/components/Auth/Login/Login';
import AuthFooter from '@/components/Auth/AuthFooter';
import { redirectToRoot } from '@/utils/handleAuth';


export default async function Login() {
    await redirectToRoot();
    return (
            <div className="flex flex-col h-full w-full">
                <div className="flex flex-nowrap h-full">
                    <div className="px-[30px] pt-[30px] flex flex-col w-full ">
                        <div className="login-form flex flex-col flex-1 items-center justify-center w-full max-w-[420px] mx-auto">
                            <div className="logo flex items-center justify-center">
                                <Image
                                    src={LoginIcon}
                                    width={42}
                                    height={42}
                                    className=" w-[36px] h-auto sm:w-[48px] object-contain"
                                    alt="Weam"
                                />
                            </div>
                            <h1 className="text-[26px] sm:text-[36px] font-semibold leading-normal mb-8 sm:mb-16 text-b2">
                                Sign In
                            </h1>
                            <LoginForm />
                        </div>
                        <AuthFooter />
                    </div>
                </div>
            </div>
    );
}
