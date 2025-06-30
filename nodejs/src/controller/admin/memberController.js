const memberService = require('../../services/member');

const getAllMembers = catchAsync(async (req, res) => {
    const result = await memberService.getAllMembers(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'member');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'member');
    return util.recordNotFound(null, res);
})

module.exports = {
    getAllMembers
}