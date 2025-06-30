const promptService = require('../../services/prompts');

const PROMPTS = 'prompt';

const addPrompt = catchAsync(async (req, res) => {
    const result = await promptService.addPrompt(req);
    if (result) {
        res.message = _localize('module.create', req, PROMPTS);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, PROMPTS), res);
})

const getPromptList = catchAsync(async (req, res) => {
    const result = await promptService.getPromptList(req);


    if (result.status === 302) {
        res.message = _localize("module.unAuthorized", req, "Prompts");
        return util.redirectResponse(res);
    }
    if (result.data.length) {
        res.message = _localize('module.list', req, PROMPTS);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.recordNotFound', req, PROMPTS);
    return util.recordNotFound(null, res);
})

const deletePrompt = catchAsync(async (req, res) => {
    const result = await promptService.deletePrompt(req);
    res.message = _localize('module.delete', req, PROMPTS);
    return util.successListResponse(result, res);
})

const updatePrompt = catchAsync(async (req, res) => {
    const result = await promptService.updatePrompt(req);
    res.message = _localize('module.update', req, PROMPTS);
    return util.successResponse(result, res);
})

const usersWiseGetAll = catchAsync(async (req, res) => {
    const result = await promptService.usersWiseGetAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, PROMPTS);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, PROMPTS);
    return util.recordNotFound(null, res);
})

const favoritePrompt = catchAsync(async (req, res) => {
    const result = await promptService.favoritePrompt(req);
    if (result) {
        if(req.body.isFavorite){
            res.message = _localize('module.favorite', req, PROMPTS);
        }else{
            res.message = _localize('module.unfavorite', req, PROMPTS);
        }
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.favoriteError', req, PROMPTS), res);
});

module.exports = {
    addPrompt,
    getPromptList,
    deletePrompt,
    updatePrompt,
    usersWiseGetAll,
    favoritePrompt
}