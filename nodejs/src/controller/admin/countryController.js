const countryService = require('../../services/country');

const addCountry = catchAsync(async (req, res) => {
    const result = await countryService.addCountry(req);
    if (result) {
        res.message = _localize('module.create', req, 'country');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'country'), res);
})

const updateCountry = catchAsync(async (req, res) => {
    const result = await countryService.updateCountry(req);
    if (result) {
        res.message = _localize('module.update', req, 'country');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'country'), res);
})

const viewCountry = catchAsync(async (req, res) => {
    const result = await countryService.viewCountry(req);
    if (result) {
        res.message = _localize('module.get', req, 'country');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'country'), res);
})

const deleteCountry = catchAsync(async (req, res) => {
    const result = await countryService.deleteCountry(req);
    if (result) {
        res.message = _localize('module.delete', req, 'country');
        return util.successResponse(null, res);
    }
    return util.failureResponse(_localize('module.deleteError', req, 'country'), res);
})

const getAll = catchAsync(async (req, res) => {
    const result = await countryService.getAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'country');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'country');
    return util.recordNotFound(null, res);
})

const partialUpdate = catchAsync(async (req, res) => {
    const result = await countryService.partialUpdate(req);
    const messageKey = result.isActive ? 'module.active' : 'module.deActive';
    res.message = _localize(messageKey, req, 'country');
    return util.successResponse(result, res);
})

module.exports = {
    addCountry,
    updateCountry,
    viewCountry,
    deleteCountry,
    getAll,
    partialUpdate
}