const shareChatService = require('../../services/sharechat');

const SHARE_CHAT = 'share chat';

const createShareChat = catchAsync(async (req, res) => {
    const result = await shareChatService.createShareChat(req);
    if (result) {
        res.message = _localize('module.create', req, SHARE_CHAT);
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, SHARE_CHAT), res);
})

const getAllShareChat = catchAsync(async (req, res) => {
    const result = await shareChatService.getAllShareChat(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, SHARE_CHAT);
        return util.successListResponse(result, res);
    } 
    res.message = _localize('module.notFound', req, SHARE_CHAT);
    return util.recordNotFound(null, res);
})

const deleteShareChats = catchAsync(async (req, res) => {
    const result = await shareChatService.deleteShareChats(req);
    if (result) {
        res.message = _localize('module.delete', req, SHARE_CHAT);
        return util.successResponse(result, res);
    } 
    return util.failureResponse(_localize('module.deleteError', req, SHARE_CHAT), res);
})

const viewShareChat = catchAsync(async (req, res) => {
    const result = await shareChatService.viewShareChat(req);
    if (result) {
        res.message = _localize('module.get', req, SHARE_CHAT);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, SHARE_CHAT), res);
})

module.exports = {
    createShareChat,
    getAllShareChat,
    deleteShareChats,
    viewShareChat
}