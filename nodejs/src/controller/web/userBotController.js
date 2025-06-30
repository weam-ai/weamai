const userBotService = require('../../services/userBot');

const USER_BOT = 'model';

const addUserBot = catchAsync(async (req, res) => {
    const result = await userBotService.addUserBot(req);
    if (result) {
        res.message = _localize('module.create', req, USER_BOT);
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, USER_BOT), res);
})

const updateUserBot = catchAsync(async (req, res) => {
    const result = await userBotService.updateUserBot(req);
    if (result) {
        res.message = _localize('module.update', req, USER_BOT);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, USER_BOT), res);
})

const viewUserBot = catchAsync(async (req, res) => {
    const result = await userBotService.viewUserBot(req);
    if (result) {
        res.message = _localize('module.get', req, USER_BOT);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, USER_BOT), res);
})

const deleteUserBot = catchAsync(async (req, res) => {
    const result = await userBotService.deleteUserBot(req);
    if (result) {
        res.message = _localize('module.delete', req, USER_BOT);
        return util.successResponse(null, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, USER_BOT), res);
})

const getAll = catchAsync(async (req, res) => {
    const result = await userBotService.getAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, USER_BOT);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.listError', req, USER_BOT);
    return util.recordNotFound(null, res);
})

const partialUpdate = catchAsync(async (req, res) => {
    const result = await userBotService.partialUpdate(req);
    const messageKey = result.isActive ? 'module.active' : 'module.deActive';
    res.message = _localize(messageKey, req, USER_BOT);
    return util.successResponse(result, res);
})

const viewApiKey = catchAsync(async (req, res) => {
    const result = await userBotService.viewApiKey(req);
    if (result) {
        res.message = _localize('module.get', req, 'api key');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'api key'), res);
})

module.exports = {
    addUserBot,
    updateUserBot,
    viewUserBot,
    deleteUserBot,
    getAll,
    partialUpdate,
    viewApiKey
}