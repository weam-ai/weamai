const permissionService = require('../../services/rolePermission');

const getPermission = catchAsync(async (req, res) => {
    const result = await permissionService.getPermission(req);
    if (result) {
        res.message = _localize('module.get', req, 'permission');
        return util.successResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'permission');
    return util.recordNotFound(null, res);
});

const updatePermission = catchAsync(async (req, res) => {
    const result = await permissionService.updatePermission(req);
    if (result) {
        res.message = _localize('module.update', req, 'permission');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'permission'));
});

const getAll = catchAsync(async (req, res) => {
    const result = await permissionService.getAll(req);
    if (result) {
        res.message = _localize('module.list', req, 'permission');
        return util.successResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'permission');
    return util.recordNotFound(null, res);
});

const getByRole = catchAsync(async (req, res) => {
    const result = await permissionService.getByRole(req);
    if (result) {
        res.message = _localize('module.get', req, 'permission');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'permission'));
});

module.exports = {
    getPermission,
    updatePermission,
    getAll,
    getByRole
}