const cityService = require('../../services/city');

const addCity = catchAsync(async (req, res) => {
    const result = await cityService.addCity(req);
    if (result) {
        res.message = _localize('module.create', req, 'city');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'city'), res);
})

const updateCity = catchAsync(async (req, res) => {
    const result = await cityService.updateCity(req);
    if (result) {
        res.message = _localize('module.update', req, 'city');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'city'), res);
})

const viewCity = catchAsync(async (req, res) => {
    const result = await cityService.viewCity(req);
    if (result) {
        res.message = _localize('module.get', req, 'city');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'city'), res);
})

const deleteCity = catchAsync(async (req, res) => {
    const result = await cityService.deleteCity(req);
    if (result) {
        res.message = _localize('module.delete', req, 'city');
        return util.successResponse(null, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, 'city'), res);
})

const getAll = catchAsync(async (req, res) => {
    const result = await cityService.getAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'city');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'city');
    return util.recordNotFound(null, res);
})

const partialUpdate = catchAsync(async (req, res) => {
    const result = await cityService.partialUpdate(req);
    const messageKey = result.isActive ? 'module.active' : 'module.deActive';
    res.message = _localize(messageKey, req, 'city');
    return util.successResponse(result, res);
})

module.exports = {
    addCity,
    updateCity,
    viewCity,
    deleteCity,
    getAll,
    partialUpdate
}