const workspaceUserService = require('../../services/workspaceuser');

const  WORKSPACE_USER = 'workspace user';

const getAllWorkSpaceUser = catchAsync(async (req, res) => {
    const result = await workspaceUserService.getAllWorkSpaceUser(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, WORKSPACE_USER);
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, WORKSPACE_USER);
    return util.recordNotFound(null, res);
});


module.exports = {
    getAllWorkSpaceUser
}

