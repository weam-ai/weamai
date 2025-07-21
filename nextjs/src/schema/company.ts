import * as yup from 'yup';
import { REGEX } from '@/utils/helper';
import { EMAIL_REGEX_MESSAGE, PASSWORD_CONFIRM_MESSAGE, PASSWORD_MIN_LENGTH_MESSAGE, PASSWORD_REGEX_MESSAGE, INVALID_EMAIL_MESSAGE } from '@/utils/constant';

export const companyDetailSchema = yup.object({
    firstName: yup.string().max(29, 'First name must be 30 characters or less.').required('Please enter your first name.'),
    lastName: yup.string().max(29, 'Last name must be 30 characters or less.').required('Please enter your last name.'),
    companyNm: yup.string().max(49, 'Company name must be 50 characters or less.').required('Please enter company name.'),
    email: yup
        .string()
        .required(EMAIL_REGEX_MESSAGE)
        .test(
            'valid-email',
            INVALID_EMAIL_MESSAGE,
            (email) => {
                const emailRegex = REGEX.EMAIL_DOMAIN_REGEX;
                const result = email ? emailRegex.test(email) : true;
                return result;
            }
        ),
    password: yup.string().min(8, PASSWORD_MIN_LENGTH_MESSAGE).matches(REGEX.PASSWORD, PASSWORD_REGEX_MESSAGE).required('Please enter your password.'),
    confirmPassword: yup.string().required('Please retype your password.').oneOf([yup.ref('password')], PASSWORD_CONFIRM_MESSAGE),
    country: yup.object().nullable().optional(),
}) 

export const companySummarySchema = yup.object({
    address: yup.string().required('please enter your address'),
    city: yup.object().nullable().required('please choose city'),
    state: yup.object().nullable().required('please choose state'),
    country: yup.object().nullable().required('please choose country.'),
    zipcode: yup.string().length(6).typeError('please enter pincode.'),
}) 

const handleError = (value, ctx) => {
    if (value?.message) {
        return ctx.createError({ message: value?.message });
    } else {
        return value;
    }
};
export const companyPaymentSchema = yup.object({
    cardNo: yup.mixed().test('cardNo', 'please enter card details', handleError),
    cardName: yup.string().max(20, 'card name must be at most 20 characters').required('please enter card holder name'),
})

export type CompanyDetailSchemaType = yup.InferType<typeof companyDetailSchema>;