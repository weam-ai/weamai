const stateService = require('../../services/state');

const addState = catchAsync(async (req, res) => {
    const result = await stateService.addState(req);
    if (result) {
        res.message = _localize('module.create', req, 'state');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'state'), res);
})

const updateState = catchAsync(async (req, res) => {
    const result = await stateService.updateState(req);
    if (result) {
        res.message = _localize('module.update', req, 'state');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'state'), res);
})

const viewState = catchAsync(async (req, res) => {
    const result = await stateService.viewState(req);
    if (result) {
        res.message = _localize('module.get', req, 'state');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'state'), res);
})

const deleteState = catchAsync(async (req, res) => {
    const result = await stateService.deleteState(req);
    if (result) {
        res.message = _localize('module.delete', req, 'state');
        return util.successResponse(null, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, 'state'), res);
})

const getAll = catchAsync(async (req, res) => {
    const result = await stateService.getAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'state');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'state');
    return util.recordNotFound(null, res);
})

const partialUpdate = catchAsync(async (req, res) => {
    const result = await stateService.partialUpdate(req);
    const messageKey = result.isActive ? 'module.active' : 'module.deActive';
    res.message = _localize(messageKey, req, 'state');
    return util.successResponse(result, res);
})

module.exports = {
    addState,
    updateState,
    viewState,
    deleteState,
    getAll,
    partialUpdate
}