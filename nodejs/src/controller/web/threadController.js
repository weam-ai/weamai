const { RESPONSE_CODE } = require('../../config/constants/common');
const threadService = require('../../services/thread');
const responseStatusCode = require('../../utils/responseCode');

const editMessage = catchAsync(async (req, res) => {
    const result = await threadService.editMessage(req);
    if (result) {
        res.message = _localize('module.update', req, 'message');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'message'), res);
})

const viewMessage = catchAsync(async (req, res) => {
    const result = await threadService.viewMessage(req);
    if (result) {
        res.message = _localize('module.get', req, 'message');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'message'), res);
})

const deleteMessage = catchAsync(async (req, res) => {
    const result = await threadService.deleteMessage(req);
    if (result) {
        res.message = _localize('module.delete', req, 'message');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, 'message'), res);
})

const getAll = catchAsync(async (req, res) => {
    const result = await threadService.getAll(req);
    if (result.data.length) {
        return res.status(responseStatusCode.success).json({
            status: responseStatusCode.success,
            code: RESPONSE_CODE.DEFAULT,
            message: _localize('module.list', req, 'message'),
            data: result.data,
            messageCount: result.messageCount,
            paginator: result.paginator,
        });
    }
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.notFound,
        code: RESPONSE_CODE.NOT_FOUND,
        message: _localize('module.notFound', req, 'message'),
        data: [],
        messageCount: result.messageCount
    });
})

const addReaction = catchAsync(async (req, res) => {
    const result = await threadService.addReaction(req);
    if (result) {
        res.message = _localize('module.update', req, 'reaction');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'reaction'), res);
})

const sendMessage = catchAsync(async (req, res) => {
    const result = await threadService.sendMessage(req);
    if (result) {
        res.message = _localize('module.create', req, 'message');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'message'), res);
})

const saveTime = catchAsync(async (req, res) => {
    const result = await threadService.saveTime(req);
    res.message = _localize('module.update', req, 'response time');
    return util.successResponse(result, res);
})

const getUserMsgCredit = catchAsync(async (req, res) => {
    const result = await threadService.getUserMsgCredit(req);
    res.message = _localize('module.get', req, 'credit');
    return util.successResponse(result, res);
})

const searchMessage = catchAsync(async (req, res) => {
    const result = await threadService.searchMessage(req);
    res.message = _localize('module.post', req, 'search');
    return util.successResponse(result, res);
})

module.exports = {
    editMessage,
    viewMessage,
    deleteMessage,
    getAll,
    addReaction,
    sendMessage,
    saveTime,
    getUserMsgCredit,
    searchMessage
}