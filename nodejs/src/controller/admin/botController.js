const botService = require('../../services/bot');

const addBot = catchAsync(async (req, res) => {
    const result = await botService.addBot(req);
    if (result) {
        res.message = _localize('module.create', req, 'bot');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'bot'));
})

const updateBot = catchAsync(async (req, res) => {
    const result = await botService.updateBot(req);
    if (result) {
        res.message = _localize('module.update', req, 'bot');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'bot'));
})

const viewBot = catchAsync(async (req, res) => {
    const result = await botService.viewBot(req);
    if (result) {
        res.message = _localize('module.get', req, 'bot');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'bot'));
})

const deleteBot = catchAsync(async (req, res) => {
    const result = await botService.deleteBot(req);
    if (result) {
        res.message = _localize('module.delete', req, 'bot');
        return util.successResponse(null, res);
    }
    return util.failureResponse('module.deleteError', req, 'bot');
})

const getAll = catchAsync(async (req, res) => {
    const result = await botService.getAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'bot');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'bot');
    return util.recordNotFound(null, res);
})

const partialUpdate = catchAsync(async (req, res) => {
    const result = await botService.partialUpdate(req);
    const messageKey = result.isActive ? 'module.active' : 'module.deActive';
    res.message = _localize(messageKey, req, 'bot');
    return util.successResponse(result, res);
})

module.exports = {
    addBot,
    updateBot,
    viewBot, 
    deleteBot,
    getAll,
    partialUpdate
}