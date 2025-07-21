import * as yup from 'yup'
import { REGEX } from '@/utils/helper'
import { EMAIL_REGEX_MESSAGE, PASSWORD_CONFIRM_MESSAGE, PASSWORD_MIN_LENGTH_MESSAGE, PASSWORD_REGEX_MESSAGE, INVALID_EMAIL_MESSAGE } from '@/utils/constant'


export const loginSchemaKeys = yup.object({
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
    password: yup.string().required('Please enter your password.'),
}) 

export const forgotPasswordKeys = yup.object({
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
        )
}) 

export const resetPasswordKeys = yup.object({
    password: yup.string().min(8, PASSWORD_MIN_LENGTH_MESSAGE).matches(REGEX.PASSWORD, PASSWORD_REGEX_MESSAGE).required('please enter your password.'),
    confirmPassword: yup.string().required('Please retype your password.').oneOf([yup.ref('password')], PASSWORD_CONFIRM_MESSAGE),
}) 

export const inviteUsersKeys = yup.object().shape({
    role: yup.object().nullable().required('Please select a role'),
});

export const onBoardLoginKeys = yup.object({
    fname: yup.string().max(29, 'First name must be 30 characters or less.').required('Please enter your first name.'),
    lname: yup.string().max(29, 'Last name must be 30 characters or less.').required('Please enter your last name.'),
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
    password: yup.string().min(8).matches(REGEX.PASSWORD, PASSWORD_REGEX_MESSAGE).required('please enter your password.'),
})

export const changePasswordKeys = yup.object({
    oldpassword: yup.string().min(8, PASSWORD_MIN_LENGTH_MESSAGE).matches(REGEX.PASSWORD, PASSWORD_REGEX_MESSAGE).required('please enter your old password.'),
    password: yup.string().min(8, PASSWORD_MIN_LENGTH_MESSAGE).matches(REGEX.PASSWORD, PASSWORD_REGEX_MESSAGE).required('please enter your password.'),
    confirmPassword: yup.string().required('Please retype your password.').oneOf([yup.ref('password')], PASSWORD_CONFIRM_MESSAGE),
})