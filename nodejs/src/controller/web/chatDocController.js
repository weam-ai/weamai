const chatDocService = require('../../services/chatdoc');

const DOCS = 'docs'

const getAllChatDocs = catchAsync(async (req, res) => {
    const result = await chatDocService.getAllChatDocs(req);

    if (result.status === 302) {
        res.message = _localize("module.unAuthorized", req, DOCS);
        return util.redirectResponse(res);
    }
    
    if (result.data.length) {
        res.message = _localize('module.list', req, DOCS);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, DOCS);
    return util.recordNotFound(null, res);
})

const deleteChatDoc = catchAsync(async (req, res) => {
    const result = await chatDocService.deleteChatDoc(req);
    if (result) {
        res.message = _localize('module.delete', req, DOCS);
        return util.successResponse(null, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, DOCS), res);
})

const usersWiseGetAll = catchAsync(async (req, res) => {
    const result = await chatDocService.usersWiseGetAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, DOCS);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, DOCS);
    return util.recordNotFound(null, res);
})

const favoriteChatDoc = catchAsync(async (req, res) => {
    const result = await chatDocService.favoriteChatDoc(req);
    if (result) {
        if(req.body.isFavorite){
            res.message = _localize('module.favorite', req, DOCS);
        }else{
            res.message = _localize('module.unfavorite', req, DOCS);
        }
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.favoriteError', req, DOCS), res);
})

module.exports = {
    getAllChatDocs,
    deleteChatDoc,
    usersWiseGetAll,
    favoriteChatDoc
}