const dashboardService = require('../../services/dashboard');
const uploadService =require('../../services/uploadFile');

const getDashboard = catchAsync(async (req, res) => {
    const result = await dashboardService.getDashboard(req);
    if (result) {
        res.message = _localize('module.get', req, 'dashboard');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'dashboard'), res);
})

const costAndUsage = catchAsync(async (req, res) => {
    const result = await uploadService.fetchS3UsageAndCost(req);
    if (result) {
        res.message = _localize('module.get', req, 'cost and usage');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'cost and usage'), res);
})

const wordUsageReport = catchAsync(async (req, res) => {
    const result = await dashboardService.wordUsageReport(req);
    if (result) {
        res.message = _localize('module.get', req, 'word usage');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'word usage'), res);
})

const workspaceOverview = catchAsync(async (req, res) => {
    const result = await dashboardService.workspaceOverview(req);
    if (result) {
        res.message = _localize('module.get', req, 'overview');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'overview'), res);
})

const getCompanyUsage = catchAsync(async (req, res) => {
    const result = await dashboardService.getCompanyUsage(req);
    if (result) {
        res.message = _localize('module.get', req, 'company usage');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'company usage'), res);
})

module.exports = {
    getDashboard,
    costAndUsage,
    wordUsageReport,
    workspaceOverview,
    getCompanyUsage
}