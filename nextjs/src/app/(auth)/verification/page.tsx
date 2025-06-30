import VerificationLink from '@/components/Auth/Register/VerificationLink';
import AuthFooter from '../../../components/Auth/AuthFooter';
import EmailIcon from '@/icons/EmailIcon';


const VerificationEmail = () => {
    return (
        <div className='flex h-full w-full flex-col'>
            <div className='flex flex-col h-full w-full items-center justify-center max-w-[450px] mx-auto text-center'>
                <span className='bg-b3 px-2 py-2 size-14 rounded-full flex justify-center items-center'>
                <EmailIcon className={"fill-b12 size-7"} />
                </span>
                <h3 className='text-font-24 mb-5 font-bold'>Verify Your Email to Continue</h3>
                <p className='mb-5'>A verification link has been sent to your email. Please click on the link to verify your email. </p>
                <VerificationLink/>
            </div>
            <AuthFooter />
        </div>
    )
}

export default VerificationEmail


