const joi = require('joi');
const { brainSchemaKeys } = require('./commonref');

const createPromptKeys = joi.object({
    title: joi.string().required(),
    content: joi.string().required(),
    brains: joi.array().items(brainSchemaKeys),
    tags: joi.array().items().required(),
    website: joi.array().items().optional(),
    summaries: joi.object().allow(null, {}),
    addinfo: joi.object().optional(),
    brandInfo: joi.object().allow(null, {}),
    companyInfo: joi.object().allow(null, {}),
    productInfo: joi.object().allow(null, {}),
    selected: joi.string().regex(/^[0-9a-fA-F]{24}$/).optional(),
    isFavorite: joi.boolean().optional(),
});

const editPromptKeys = joi.object({
    title: joi.string().required(),
    content: joi.string().required(),
    brains: joi.array().items(brainSchemaKeys),
    tags: joi.array().items().required(),
    website: joi.array().items().optional(),
    summaries: joi.object().allow(null, {}),
    addinfo: joi.object().optional(),
    brandInfo: joi.object().allow(null, {}),
    companyInfo: joi.object().allow(null, {}),
    productInfo: joi.object().allow(null, {}),
    selected: joi.string().regex(/^[0-9a-fA-F]{24}$/).required(),
    isFavorite: joi.boolean().optional(),
});

module.exports = {
    createPromptKeys,
    editPromptKeys
};
