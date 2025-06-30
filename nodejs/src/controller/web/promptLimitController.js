const promptlimitService = require('../../services/promptlimit');

const setPromptLimit = catchAsync(async (req, res) => {
    const result = await promptlimitService.setPromptLimit(req);
    if (result) {
        res.message = _localize('module.update', req, 'prompt limit');
        return util.successResponse(result, res);
    }
    return util.failureResponse(
        _localize('module.updateError', req, 'prompt limit'),
    );
});

module.exports = {
    setPromptLimit,
};
