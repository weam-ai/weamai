const joi = require('joi');

const updatePermissionKeys = joi.object({
    roleId: joi.string().regex(/^[0-9a-fA-F]{24}$/).required(),
    permissionIds: joi.array().required(),
})

module.exports = {
    updatePermissionKeys
}