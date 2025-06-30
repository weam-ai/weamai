'use client';

import { useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import routes from '@/utils/routes';

export const LoginButton = () => {
    const router = useRouter();
    const submitChange = () => {
        router.push(routes.login);
    };
    return (
        <button
            type="submit"
            className="btn btn-blue btn-lg px-16 mt-6"
            onClick={submitChange}
        >
            Login Now
        </button>
    );
};

export const Welcome = () => {
    const data = useSelector((store:any) => store.signup.details);
    return (
        <h2 className="text-center max-w-[550px] mx-auto text-[30px] font-semibold leading-normal mb-4 text-b2">
            Welcome Aboard, <span className="text-blue">{data.companyNm}</span>
            <br /> Thank you for choosing Weam
        </h2>
    );
};
