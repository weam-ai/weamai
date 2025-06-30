const joi = require('joi');
const { companySchemaKeys, botSchemaKeys } = require('./commonref');

const addBotKeys = joi.object({
    title: joi.string().required(),
    modelType: joi.number().required(),
});

const updateBotKeys = joi.object({
    title: joi.string().required(),
});

const createUserBotKeys = joi.object({
    bot: joi.object(botSchemaKeys).required(),
    config: joi.object({
        apiKey: joi.string().required(),
    }).required()
});

const updateUserBotKeys = joi.object({
    bot: joi.object(botSchemaKeys).required(),
    company: joi.object(companySchemaKeys).required(),
    config: joi.object({
        apikey: joi.string().required(),
    }).required(),
});

const updateChatKeys = joi.object({
    botId: joi
        .string()
        .regex(/^[0-9a-fA-F]{24}$/)
        .required(),
    msg: joi.string().required(),
})

const viewApiKeys = joi.object({
    apikey: joi.string().required()
})

const removeUserBotKeys = joi.object({
    code: joi.string().required(),
})

module.exports = {
    addBotKeys,
    updateBotKeys,
    createUserBotKeys,
    updateUserBotKeys,
    updateChatKeys,
    viewApiKeys,
    removeUserBotKeys
};
