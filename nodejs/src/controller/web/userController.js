const userService = require('../../services/user');

const storageDetails = catchAsync(async (req, res) => {
    const result = await userService.storageDetails(req);
    res.message = _localize('module.get', req, 'storage details');
    return util.successResponse(result, res);
});

const storageIncrease = catchAsync(async (req, res) => {
    const result = await userService.storageIncreaseRequest(req);
    res.message = _localize('module.storageRequest', req);
    return util.successResponse(result, res);
});

const getUser = catchAsync(async (req, res) => {
    const result = await userService.getUser(req);
    if (result) {
        res.message = _localize('module.get', req, 'user');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'user'), res);
})

const userFavoriteList = catchAsync(async (req, res) => {
    const result = await userService.userFavoriteList(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'user favorite list');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'user favorite list');
    return util.recordNotFound(null, res);
})

module.exports = {
    storageDetails,
    storageIncrease,
    getUser,
    userFavoriteList
}