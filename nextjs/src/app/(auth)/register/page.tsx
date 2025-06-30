import React from 'react';
import 'rc-steps/assets/index.css';
import AuthFooter from '../../../components/Auth/AuthFooter';
import RegisterIcon from '../../../../public/register.svg';
import Image from 'next/image';
import { RegisterNavigation } from '@/components/Auth/Register/Register';
import { redirectToRoot } from '@/utils/handleAuth';
const MultiStepForm = async () => {
    await redirectToRoot();
    return (
        <div className="flex flex-col h-full w-full">
            <div className="flex flex-nowrap h-full">
                <div className="px-[30px] pt-[30px] flex flex-col w-full ">
                    <div className="login-form flex flex-col flex-1 items-center justify-center w-full max-w-[650px] mx-auto">
                        <div className="logo flex items-center justify-center">
                            <Image
                                src={RegisterIcon}
                                width={42}
                                height={42}
                                className=" w-[34px] h-auto sm:w-[42px] object-contain"
                                alt="Weam"
                            />
                        </div>
                            <h1 className="text-[26px] sm:text-[36px] font-semibold leading-normal mb-8 sm:mb-10 text-b2">
                                Sign Up
                            </h1>
                            <RegisterNavigation />
                        </div>
                    <AuthFooter />
                </div>
            </div>
        </div>
    );
};

export default MultiStepForm;
