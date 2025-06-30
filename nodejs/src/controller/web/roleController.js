const roleService = require('../../services/role');

const getAllRole = catchAsync(async (req, res) => {
    const result = await roleService.getAllRole(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'role');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'role');
    return util.recordNotFound(null, res);
})

module.exports = {
    getAllRole
}