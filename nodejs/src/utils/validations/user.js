const joi = require('joi');

const createSchemaKeys = joi.object({
    username: joi.string().required(),
    email: joi.string().email().required(),
    roleId: joi.string().regex(/^[0-9a-fA-F]{24}$/).required(),
    roleCode: joi.string().required(),
})

const updateSchemaKeys = joi.object({
    fname: joi.string().optional(),
    lname: joi.string().optional(),
}).unknown(true);

const storageRequestKeys = joi.object({
    requestSize: joi.number().required()
})

const updateCreditKeys = joi.object({
    email: joi.string().email().required(),
    credit: joi.number().required()
})

module.exports = {
    createSchemaKeys,
    updateSchemaKeys,
    storageRequestKeys,
    updateCreditKeys,
}