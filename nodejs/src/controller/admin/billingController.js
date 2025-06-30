const billingService = require('../../services/billing');

const getAllMembers = catchAsync(async (req, res) => {
    const result = await billingService.getAllMembers(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'billing member');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'billing member');
    return util.recordNotFound(null, res);
})

module.exports = {
    getAllMembers
}