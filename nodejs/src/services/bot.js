const Bot = require('../models/bot');
const dbService = require('../utils/dbService');
const { convertCodeFormat } = require('../utils/helper');

async function addBot(req) {
    try {
        const { title } = req.body;
        const existingBot = await dbService.getDocumentByQuery(Bot, { title: title });
        if (existingBot) {
            throw new Error(_localize('module.alreadyExists', req, 'bot'));
        }
        req.body.code = convertCodeFormat(title);
        return dbService.createDocument(Bot, req.body);
    } catch (error) {
        handleError(error, 'Error - addBot');
    }
}

async function checkBot(req) {
    const result = await Bot.findById({ _id: req.params.id });
    if (!result) {
        throw new Error(_localize('module.notFound', req, 'bot'));
    }
    return result;
}

async function updateBot(req) {
    try {
        await checkBot(req);
        return Bot.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true });
    } catch (error) {
        handleError(error, 'Error - updateBot');
    }
}

async function viewBot(req) {
    try {
        return checkBot(req);
    } catch (error) {
        handleError(error, 'Error - viewBot');
    }
}

async function deleteBot(req) {
    try {
        await checkBot(req);
        return Bot.deleteOne({ _id: req.params.id });
    } catch (error) {
        handleError(error, 'Error - deleteBot');
    }
}

async function getAll(req) {
    try {
        return dbService.getAllDocuments(Bot, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error - getAll');
    }
}

async function partialUpdate(req) {
    try {
        return Bot.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).select('isActive');
    } catch (error) {
        handleError(error, 'Error - partialUpdate');
    }
}

module.exports = {
    addBot,
    updateBot,
    viewBot,
    deleteBot,
    getAll,
    partialUpdate
}