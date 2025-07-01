const storageRequestService = require('../../services/storageRequest');

const getAllStorageRequest = async (req, res) => {
    const result = await storageRequestService.getAllStorageRequest(req);
    
    if (result.data.length) {
        res.message = _localize('module.list', req, 'Storage request');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'Storage request');
    return util.recordNotFound(null, res);
};

const declineStorageRequest = async (req, res) => {
    const result = await storageRequestService.declineStorageRequest(req);

    if (result) {
        res.message = _localize('module.storageRequestDecline', req, '');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.storageRequestUpdateError', req, ''), res);
};

const approveStorageRequest = async (req, res) => {
    const result = await storageRequestService.approveStorageRequest(req);
    if (result) {
        res.message = _localize('module.storageRequestAccept', req, '');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.storageRequestUpdateError', req, ''), res);
};

// Exporting the controller functions
module.exports = {
    getAllStorageRequest,
    declineStorageRequest,
    approveStorageRequest
};
