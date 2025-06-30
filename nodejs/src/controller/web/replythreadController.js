const replyThreadService = require('../../services/replythread');

const CONVERSATION = 'conversation';

const sendMessage = catchAsync(async (req, res) => {
    const result = await replyThreadService.sendMessage(req);
    if (result) {
        res.message = _localize('module.create', req, CONVERSATION);
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, CONVERSATION), res);
})

const getReplayThreadList = catchAsync(async (req, res) => {
    const result = await replyThreadService.getReplayThreadList(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, CONVERSATION);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.recordNotFound', req, CONVERSATION);
    return util.recordNotFound(null, res);
})

module.exports = {
    sendMessage,
    getReplayThreadList
}