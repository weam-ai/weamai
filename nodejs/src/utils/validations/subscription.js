const joi = require('joi');

const couponCodeKeys = joi.object({
    coupon: joi.any().invalid(null, '').messages({ 'any.invalid': 'Please enter coupon code' })
})

const createStripeCustomerKeys = joi.object({
    payment_method: joi.string().required(),
    price_id: joi.string().required(),
    coupon: joi.string().allow(null).optional(),
    quantity: joi.number().required(),
    plan_name: joi.string().required(),
    notes: joi.object().required()
})

const storageRequestChargeKeys = joi.object({
    storageRequestId: joi.string().required(),
    updatedStorageSize: joi.number().required(),
    amount: joi.number().integer().min(1).required(),
    currency: joi.string().required()
})

const updatePaymentMethodKeys = joi.object({
    paymentMethodId: joi.string().required()
})

const updateSubscriptionKeys = joi.object({
    price_id: joi.string().required(),
    quantity: joi.number().required(),
    coupon: joi.string().allow(null).optional(),
    notes: joi.object().required()
})

const cancelSubscriptionKeys = joi.object({
    cancel_reason: joi.string().allow('').optional()
})

module.exports = {
    couponCodeKeys,
    createStripeCustomerKeys,
    storageRequestChargeKeys,
    updatePaymentMethodKeys,
    updateSubscriptionKeys,
    cancelSubscriptionKeys
}
