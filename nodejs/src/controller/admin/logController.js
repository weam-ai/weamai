const logService = require('../../services/log');

const activityLogList = catchAsync(async (req, res) => {
    const result = await logService.activityLogList(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'activity log');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'activity log');
    return util.recordNotFound(null, res);
})

module.exports = {
    activityLogList
}