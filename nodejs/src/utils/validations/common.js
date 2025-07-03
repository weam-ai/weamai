const joi = require('joi');
const { countrySchemaKeys, updateCountrySchemaKeys, stateSchemaKeys, updateStateSchemaKeys, citySchemaKeys, userSchemaKeys } = require('./commonref');
const { PASSWORD_REGEX } = require('../../config/constants/common');

const partialUpdateKeys = joi.object({
    isActive: joi.boolean().required()
}).unknown(false);

const countryCreateKeys = joi.object({
    nm: joi.string().required(),
    code: joi.string().required(),
    dialCode: joi.string().required(),
})

const countryUpdateKeys = joi.object({
    nm: joi.string().required(),
    code: joi.string().required(),
    dialCode: joi.string().required(),
})

const stateCreateKeys = joi.object({
    nm: joi.string().required(),
    code: joi.string().required(),
    country: joi.object(countrySchemaKeys).required(),
})

const stateUpdateKeys = joi.object({
    nm: joi.string().required(),
    code: joi.string().required(),
    country: joi.object(updateCountrySchemaKeys).required(),
})

const cityCreateKeys = joi.object({
    nm: joi.string().required(),
    code: joi.string().required(),
    country: joi.object(countrySchemaKeys).required(),
    state: joi.object(stateSchemaKeys).required(),
})

const cityUpdateKeys = joi.object({
    nm: joi.string().required(),
    code: joi.string().required(),
    country: joi.object(updateCountrySchemaKeys).required(),
    state: joi.object(updateStateSchemaKeys).required(),
})

const manualNotificationKeys = joi.object({
    token: joi.string().required()
})

const companyCreateKeys = joi.object({
    fname: joi.string().required(),
    lname: joi.string().required(),
    email: joi
    .string()
    .email()
    .lowercase()
    .required(),
    password: joi
        .string()
        .min(8)
        .required()
        .regex(PASSWORD_REGEX)
        .message(
            'Your password should contain one uppercase letter, numeric and special characters'
        ),
    confirmPassword: joi.ref('password'),
    companyNm: joi.string().required(),
    countryName: joi.string().optional(),
    countryCode: joi.string().optional(),
}).options({ abortEarly: true });

const companyUpdateKeys = joi.object({
    companyNm: joi.string().required(),
    billingAdd: joi
        .object({
            line1: joi.string().required(),
            line2: joi.string().optional(),
            country: joi.object(countrySchemaKeys).required(),
            state: joi.object(stateSchemaKeys).required(),
            city: joi.object(citySchemaKeys).required(),
            zipcode: joi.string().optional(),
        })
        .required(),
    renewDate: joi.date().required(),
    renewAmt: joi.number().required(),
});

const emailTemplateKeys = joi.object({
    nm: joi.string().required(),
    code: joi.string().required(),
    subject: joi.string().required(),
    body: joi.string().required(),
    htmlPath: joi.string().required(),
    cssPath: joi.string().required(),
})

const kafkaTopicKeys = joi.object({
    topic: joi.string().required(),
    partition: joi.number().required()
})

const setPromptLimitKeys = joi.object({
    day: joi.number().required(),
    week: joi.number().required(),
    month: joi.number().required(),
})

const addTeamMembersKeys = joi.object({
    users: joi
        .array()
        .items({
            email: joi.string().email().required(),
            roleId: joi
                .string()
                .regex(/^[0-9a-fA-F]{24}$/)
                .required(),
            roleCode: joi.string().required(),
        })
        .required(),
});

const checkApiKeys = joi.object({
    key: joi.string().required(),
    code: joi.string().required(),
})

const resendVerification = joi.object({
    email: joi.string().email().lowercase().required(),
    minutes: joi.number().optional()
})

module.exports = {
    partialUpdateKeys,
    countryCreateKeys,
    countryUpdateKeys,
    stateCreateKeys,
    stateUpdateKeys,
    cityCreateKeys,
    cityUpdateKeys,
    manualNotificationKeys,
    companyUpdateKeys,
    emailTemplateKeys,
    kafkaTopicKeys,
    setPromptLimitKeys,
    companyCreateKeys,
    addTeamMembersKeys,
    checkApiKeys,
    resendVerification
}