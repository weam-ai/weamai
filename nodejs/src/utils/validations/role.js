const joi = require('joi');

const createRoleSchemaKeys = joi.object({
    name: joi.string().required(),
    code: joi.string().required(),
})

const updateRoleSchemaKeys = joi.object({
    name: joi.string().required(),
    code: joi.string().required(),
    isActive: joi.boolean().optional()
})

module.exports = {
    createRoleSchemaKeys,
    updateRoleSchemaKeys
}