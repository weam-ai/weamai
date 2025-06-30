const invoiceService = require('../../services/invoice');

const getInvoice = catchAsync(async (req, res) => {
    const result = await invoiceService.getInvoice(req);
    if (result) {
        res.message = _localize('module.list', req, 'invoice');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

module.exports = { getInvoice };