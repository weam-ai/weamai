const joi = require('joi');
const { PASSWORD_REGEX } = require('../../config/constants/common');

const PASSWORD_REGEX_MESSAGE = 'Your password should contain one uppercase letter, numeric and special characters';

const commonSignupKeys = joi.object({
    users: joi.array().items(joi.object({
        email: joi.string().email().lowercase().required(),
    })).required(),
    roleCode: joi.string().required(),
});

const signInSchemaKeys = joi.object({
    email: joi.string().email().lowercase().required(),
    password: joi
        .string()
        .required()
});

const changePasswordKeys = joi.object({
    oldpassword: joi
        .string()
        .required()
        .regex(PASSWORD_REGEX)
        .message(PASSWORD_REGEX_MESSAGE),
    newpassword: joi
        .string()
        .required()
        .regex(PASSWORD_REGEX)
        .message(PASSWORD_REGEX_MESSAGE),
});

const forgotPasswordKeys = joi.object({
    email: joi.string().email().lowercase().required()
});

const resendOtpKeys = joi.object({
    email: joi.string().email().required(),
});

const verifyOtpKeys = joi.object({
    email: joi.string().email().optional(),
    otp: joi.string().required(),
});

const resetPasswordKeys = joi.object({
    id: joi.string().regex(/^[0-9a-fA-F]{24}$/).required(),
    resetHash: joi.string().optional(),
    password: joi
        .string()
        .required()
        .regex(PASSWORD_REGEX)
        .message(PASSWORD_REGEX_MESSAGE),
});

const inviteLoginKeys = joi.object({
    inviteLink: joi.string().required(),
})

const logoutKeys = joi.object({
    fcmToken: joi.string().required(),
})

const mfaStatusKeys = joi.object({
    mfa: joi.boolean().required(),
})

const mfaLogin = joi.object({
    otp: joi.string().required()
})

const onBoardProfileKeys = joi.object({
    email: joi.string().email().lowercase().required(),
    fname: joi.string().required(),
    lname: joi.string().required(),
    password: joi.string().required()
})

module.exports = {
    signInSchemaKeys,
    changePasswordKeys,
    forgotPasswordKeys,
    verifyOtpKeys,
    resendOtpKeys,
    resetPasswordKeys,
    commonSignupKeys,
    inviteLoginKeys,
    logoutKeys,
    mfaStatusKeys,
    mfaLogin,
    onBoardProfileKeys
};
