const joi = require('joi');

const s3FileDelete = joi.object({
    key: joi.string().required(),
})

const generatePresignedUrl = joi.object({
    fileKey: joi.array().items(joi.object({
        key: joi.string().required(),
        type: joi.string().required(),
    })).required(),
    folder: joi.string().required(),
})

module.exports = {
    s3FileDelete,
    generatePresignedUrl
}