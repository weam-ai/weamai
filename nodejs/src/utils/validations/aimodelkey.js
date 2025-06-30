const joi = require('joi');

const huggingFaceAuthKeys = joi.object({
    name: joi.string().required(),
    taskType: joi.string().required(),
    apiType: joi.string().required(),
    description: joi.string().optional().allow(''),
    endpoint: joi.string().required(),
    repo: joi.string().required(),
    tool: joi.boolean().required(),
    context: joi.number().required(),
    sample: joi.boolean().required(),
    topK: joi.number().required(),
    topP: joi.number().required(),
    typicalP: joi.number().required(),
    repetitionPenalty: joi.number().required(),
    frequencyPenalty: joi.number().required(),
    temperature: joi.number().required(),
    sequences: joi.string().optional().allow(''),
    key: joi.string().required(),
    bot: joi.object({
        title: joi.string().required(),
        code: joi.string().required(),
        id: joi.string().regex(/^[0-9a-fA-F]{24}$/).required(),
    }).required(),
    numInference: joi.number().required(),
    gScale: joi.number().required(),
})

const anthropicAuthKeys = joi.object({
    key: joi.string().required(),
    bot: joi.object({
        title: joi.string().required(),
        code: joi.string().required(),
        id: joi.string().regex(/^[0-9a-fA-F]{24}$/).required(),
    }).required()
})

module.exports = {
    huggingFaceAuthKeys,
    anthropicAuthKeys
}
