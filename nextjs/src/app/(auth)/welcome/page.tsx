import React from 'react';
import Image from 'next/image';
import RoundCheckIcon from '../../../../public/round-check.svg';
import AuthFooter from '@/components/Auth/AuthFooter';
import { LoginButton, Welcome } from '@/components/Auth/Welcome';

export default function ThankYou() {
    return (
        <>
            <div className="thank-you-bg flex flex-col h-full w-full bg-cover bg-no-repeat">
                <div className="px-[30px] pt-[30px] flex flex-col w-full h-full">
                    <div className="forgot-password-form flex flex-col flex-1 items-center justify-center w-full max-w-[620px] mx-auto">
                        <Image
                            src={RoundCheckIcon}
                            width={92}
                            height={80}
                            className="w-[92px] h-[80px] object-contain mb-5"
                            alt="Welcome to Weam"
                        />
                        <Welcome />
                        <p className="text-center text-font-16 text-b5 max-w-[620px] mx-auto">
                        Thank you for choosing Weam. We are excited to have you on board and to help you unlock the power of AI collaboration! 
                        
                        </p>
                        <p className="text-center text-font-16 text-b5 font-semibold max-w-[620px] mx-auto mt-3">
                            Here s what you can do next:
                        </p>
                        <LoginButton />
                    </div>
                    <AuthFooter />
                </div>
            </div>
        </>
    );
}
