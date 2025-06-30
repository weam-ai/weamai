const roleService = require('../../services/role');


const addRole = catchAsync(async (req, res) => {
    const result = await roleService.addRole(req);
    if (result) {
        res.message = _localize('module.create', req, 'role');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'role'), res);
})

const updateRole = catchAsync(async (req, res) => {
    const result = await roleService.updateRole(req);
    if (result) {
        res.message = _localize('module.update', req, 'role');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'role'), res);
})

const getRole = catchAsync(async (req, res) => {
    const result = await roleService.getRole(req);
    if (result) {
        res.message = _localize('module.get', req, 'role');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'role'), res);
})

const deleteRole = catchAsync(async (req, res) => {
    const result = await roleService.deleteRole(req);
    if (result) {
        res.message = _localize('module.delete', req, 'role');
        return util.successResponse(null, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, 'role'), res);
})

const getAllRole = catchAsync(async (req, res) => {
    const result = await roleService.getAllRole(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'role');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'role');
    return util.recordNotFound(null, res);
})

const partialUpdate = catchAsync(async (req, res) => {
    const result = await roleService.partialUpdate(req);
    const messageKeys = result.isActive ? 'module.active' : 'module.deActive';
    res.message = _localize(messageKeys, req, 'role');
    return util.successResponse(result, res);
})

module.exports = {
    addRole,
    updateRole,
    deleteRole,
    getAllRole,
    getRole,
    partialUpdate
}