const workspaceuserService = require('../../services/workspaceuser');

const  WORKSPACE_USER = 'workspace user'
const getAllWorkSpaceUser = catchAsync(async (req, res) => {
    const result = await workspaceuserService.getAllWorkSpaceUser(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, WORKSPACE_USER);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, WORKSPACE_USER);
    return util.recordNotFound(null, res);
});

const addWorkSpaceUser = catchAsync(async (req, res) => {
    const result = await workspaceuserService.addWorkSpaceUser(req);
    if (result) {
        res.message = _localize('module.share', req, "user");
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, WORKSPACE_USER), res);
});

const deleteWorkSpaceUser = catchAsync(async (req, res) => {
    const result = await workspaceuserService.deleteWorkSpaceUser(req);
    res.message = _localize('module.unshare', req, "user");
    return util.createdDocumentResponse(result, res);
});

module.exports = {
    getAllWorkSpaceUser,
    addWorkSpaceUser,
    deleteWorkSpaceUser
}