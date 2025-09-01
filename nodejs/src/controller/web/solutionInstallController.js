const solutionInstallService = require('../../services/solutionInstall');

const install = catchAsync(async (req, res) => {
    const result = await solutionInstallService.install(req);
    res.message = _localize('module.create', req, 'solution install');
    return util.successResponse(result, res);
});

module.exports = {
    install
}


