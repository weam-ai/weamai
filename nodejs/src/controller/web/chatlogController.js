const chatService = require('../../services/chat');

const updateChat = catchAsync(async (req, res) => {
    const result = await chatService.updateChat(req);
    if (result) {
        res.message = _localize('module.update', req, 'chat log');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'chat log'));
})

const viewChat = catchAsync(async (req, res) => {
    const result = await chatService.viewChat(req);
    if (result) {
        res.message = _localize('module.get', req, 'chat log');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'chat log'));
})

const deleteChat = catchAsync(async (req, res) => {
    const result = await chatService.deleteChat(req);
    if (result) {
        res.message = _localize('module.delete', req, 'chat log');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, 'chat log'));
})

const getAll = catchAsync(async (req, res) => {
    const result = await chatService.getAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'chat log');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'chat log');
    return util.recordNotFound(null, res);
})

module.exports = {
    updateChat,
    viewChat,
    deleteChat,
    getAll
}