const reportService = require('../../services/report');

const getCompanyUsage = catchAsync(async (req, res) => {
    const result = await reportService.getCompanyUsage(req);
    if (result) {
        res.message = _localize('module.list', req, 'company usage');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'company usage');
    return util.recordNotFound(null, res);
})

const getUserUsage = catchAsync(async (req, res) => {
    const result = await reportService.getUserUsage(req);
    if (result) {
        res.message = _localize('module.list', req, 'user usage');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'user usage');
    return util.recordNotFound(null, res);
})

const getWeeklyUsage = catchAsync(async (req, res) => {
    const result = await reportService.getWeeklyUsage(req);
    if (result) {
        res.message = _localize('module.list', req, 'weekly usage');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'weekly usage');
    return util.recordNotFound(null, res);
})

module.exports = {
    getCompanyUsage,
    getUserUsage,
    getWeeklyUsage
}