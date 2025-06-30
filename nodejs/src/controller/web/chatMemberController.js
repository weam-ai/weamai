const chatMemberService = require('../../services/chatmember');

const CHAT_MEMBER = 'chat member';

const addChatMember = catchAsync(async (req, res) => {
    const result = await chatMemberService.addChatMember(req);
    if (result) {
        res.message = _localize('module.create', req, CHAT_MEMBER);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, CHAT_MEMBER), res);
})

const removeChatMember = catchAsync(async (req, res) => {
    const result = await chatMemberService.removeChatMember(req);
    if (result) {
        res.message = _localize('module.delete', req, 'Chat');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, CHAT_MEMBER), res);
})

const memberList = catchAsync(async (req, res) => {
    const result = await chatMemberService.memberList(req);

    if (result.status === 302) {
        res.message = _localize("module.unAuthorized", req, "Chats");
        return util.redirectResponse(res);
    }
    if (result.data.length) {
        res.message = _localize('module.list', req, CHAT_MEMBER);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.recordNotFound', req, CHAT_MEMBER);
    return util.recordNotFound(null, res);
})

const favouriteChat = catchAsync(async (req, res) => {
    const result = await chatMemberService.favouriteChat(req);
    const messageKey = result.isFavourite ? 'module.favorite' : 'module.unfavorite';
    res.message = _localize(messageKey, req, { '{module}': 'Chat', '{module2}': 'favourite' });
    return util.successResponse(result, res);
})

module.exports = {
    addChatMember,
    removeChatMember,
    memberList,
    favouriteChat
}