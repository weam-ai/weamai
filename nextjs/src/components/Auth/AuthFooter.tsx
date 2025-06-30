import React from 'react';
import Image from 'next/image';
import Link from 'next/link';
import WeamLogo from '../Shared/WeamLogo';
import routes from '@/utils/routes';

const AuthFooter = () => {
    return (
        <div className="login-footer flex flex-col items-center justify-center mt-auto pb-5">
            <Link href={routes.main} className="mb-4">
                <WeamLogo
                    className={'w-[90px] object-contain mr-2'}
                    height={'auto'}
                    width={90}
                />
            </Link>
            <ul className="list-none m-0 p-0 flex items-center justify-center *:px-[15px] *:border-r *:border-r-b6">
                <li className="last:border-r-0">
                    <Link
                        href="https://weam.ai/terms-conditions/"
                        target="_blank"
                        className="text-font-14 leading-none text-b6 font-normal hover:text-b2"
                    >
                        Terms of use
                    </Link>
                </li>
                <li className="last:border-r-0">
                    <Link
                        href="https://weam.ai/privacy-policy/"
                        target="_blank"
                        className="text-font-14 leading-none text-b6 font-normal hover:text-b2"
                    >
                        Privacy Policy
                    </Link>
                </li>
            </ul>
        </div>
    );
};

export default AuthFooter;
