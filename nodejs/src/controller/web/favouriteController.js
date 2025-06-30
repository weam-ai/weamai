const favouriteService = require('../../services/favourite');

const addFavourite = catchAsync(async (req, res) => {
    const result = await favouriteService.addFavourite(req);
    if (result) {
        res.message = _localize('module.create', req, 'favourite');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'favourite'), res);
})

const removeFavourite = catchAsync(async (req, res) => {
    const result = await favouriteService.removeFavourite(req);
    if (result) {
        res.message = _localize('module.delete', req, 'favourite');
        return util.successResponse(null, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, 'favourite'), res);
})

const viewFavourite = catchAsync(async (req, res) => {
    const result = await favouriteService.viewFavourite(req);
    if (result) {
        res.message = _localize('module.get', req, 'favourite');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'favourite'), res);
})

const getAll = catchAsync(async (req, res) => {
    const result = await favouriteService.getAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'favourite');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'favourite');
    return util.recordNotFound(null, res);
})

module.exports = {
    addFavourite,
    removeFavourite,
    getAll,
    viewFavourite
}