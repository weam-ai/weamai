const joi = require('joi');
const { companySchemaKeys } = require('./commonref');

const createCustomerKeys = joi.object({
    email: joi.string().email().required(),
    price : joi.number().required(),
    company: joi.object(companySchemaKeys).required(),
    source: joi.string().required(),
    address: joi.object({
        line1: joi.string().required(),
        city: joi.string().required(),
        country: joi.string().required(),
        state: joi.string().required(),
        postal_code: joi.string().required()
    }).required()
});

const createCardKeys = joi.object({
    cardname: joi.string().required(),
    cardno: joi.number().required(),
    exp_month: joi.string().required(),
    exp_year: joi.number().required(),
    cvc: joi.number().required(),
    customerId: joi.string().required(),
});

const deleteCardKeys = joi.object({
    customerId: joi.string().required(),
    cardId: joi.number().required(),
});

const updateCardKeys = joi.object({
    cardName: joi.string().required(),
    customerId: joi.number().required(),
    exp_month: joi.number().required(),
    exp_year: joi.number().required(),
    cardId: joi.number().required(),
});

const createChargesKeys = joi.object({
    email: joi.string().email().required(),
    amount: joi.number().required(),
    currency: joi.number().required(),
    card: joi.number().required(),
    customer: joi.string().required(),
});

const checkoutSessionKeys = joi.object({
    plan: joi.number().required(),
    userId: joi.string().regex(/^[0-9a-fA-F]{24}$/).required(),
});

const resumeSubscriptionKeys = joi.object({
    subscriptionId: joi.string().required(),
});

const cancelSubscriptionKeys = joi.object({
    subscriptionId: joi.string().required(),
});

module.exports = {
    createCustomerKeys,
    createCardKeys,
    deleteCardKeys,
    updateCardKeys,
    createChargesKeys,
    checkoutSessionKeys,
    resumeSubscriptionKeys,
    cancelSubscriptionKeys,
};
