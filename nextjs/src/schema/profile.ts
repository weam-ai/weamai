import * as yup from 'yup';

export const profileSchema = () => yup.object({
    fname: yup.string().required('First Name is required'),
    lname: yup.string().required('Last Name is required'),     
});

export const twoFactorAuthSchema = yup.object().shape({
    verifycode: yup.string().required('Please enter a verification code'),
});
