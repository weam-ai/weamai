const joi = require('joi');

const addFavouriteKeys = joi.object({
    username: joi.string().required(),
    threadMsg: joi.string().required(),
    threadId: joi
        .string()
        .regex(/^[0-9a-fA-F]{24}$/)
        .required(),
    aiResponse: joi.string().optional(),
});

const removeFavouriteKeys = joi.object({
    threadId: joi
        .string()
        .regex(/^[0-9a-fA-F]{24}$/)
        .required(),
});

module.exports = {
    addFavouriteKeys,
    removeFavouriteKeys
};
