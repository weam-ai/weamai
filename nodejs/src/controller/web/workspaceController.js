const workspaceService = require('../../services/workspace');

const WORKSPACE = 'workspace';

const addWorkSpace = catchAsync(async (req, res) => {
    const result = await workspaceService.addWorkSpace(req);
    if (result) {
        res.message = _localize('module.create', req, WORKSPACE);
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, WORKSPACE), res);
});

const updateWorkSpace = catchAsync(async (req, res) => {
    const result = await workspaceService.updateWorkSpace(req);
    if (result) {
        res.message = _localize('module.update', req, WORKSPACE);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, WORKSPACE), res);
});

const getWorkSpace = catchAsync(async (req, res) => {
    const result = await workspaceService.getWorkSpace(req);
    if (result) {
        res.message = _localize('module.get', req, WORKSPACE);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, WORKSPACE), res);
});

const deleteWorkSpace = catchAsync(async (req, res) => {
    const result = await workspaceService.deleteWorkSpace(req);
    if (result) {
        res.message = _localize('module.delete', req, WORKSPACE);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, WORKSPACE), res);
});

const getAllWorkSpace = catchAsync(async (req, res) => {
    const result = await workspaceService.getAllWorkSpace(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, WORKSPACE);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, WORKSPACE);
    return util.recordNotFound(null, res);
});

const partialUpdate = catchAsync(async (req, res) => {
    const result = await workspaceService.partialUpdate(req);
    const messageKey = result.isActive ? 'module.active' : 'module.deActive';
    res.message = _localize(messageKey, req, WORKSPACE);
    return util.successResponse(result, res);
});

module.exports = {
    addWorkSpace,
    updateWorkSpace,
    deleteWorkSpace,
    getAllWorkSpace,
    partialUpdate,
    getWorkSpace
}

