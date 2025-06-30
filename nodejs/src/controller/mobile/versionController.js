const { SETTING_CODE } = require('../../config/constants/common');
const Setting = require('../../models/setting');

const MOBILE = 'mobile version';

const getMobileVersion = catchAsync(async (req, res) => {
    const result = await Setting.findOne({ code: SETTING_CODE.MOBILE_VERSION }, { details: 1, _id: 0 });
    if (result) {
        res.message = _localize('module.get', req, MOBILE);
        return util.successResponse(result.details, res);
    }
    return util.failureResponse(_localize('module.getError', req, MOBILE), res);
});

module.exports = {
    getMobileVersion,
};