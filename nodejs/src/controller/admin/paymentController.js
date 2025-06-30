const paymentService = require('../../services/payment');

const createCustomer = catchAsync(async (req, res) => {
    const result = await paymentService.createCustomer(req);
    if (result) {
        res.message = _localize('module.create', req, 'Subscription');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(
        _localize('module.createError', req, 'Subscription'),
        res,
    );
});

// const transactionList = catchAsync(async (req, res) => {
//     const result = await paymentService.transactionList(req, true);
//     if (result) {
//         res.message = _localize('module.list', req, 'transaction');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(_localize('module.listError', req, 'transaction'), res);
// })

const upcomingInvoice = catchAsync(async (req, res) => {
    const result = await paymentService.upcomingInvoice(req);
    if (result) {
        res.message = _localize('module.get', req, 'Upcoming Invoice');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
});

// const managePastInvoice = catchAsync(async (req, res) => {
//     const result = await paymentService.managePastInvoice(req, true);
//     if (result) {
//         res.message = _localize('module.list', req, 'past invoice');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(_localize('module.listError', req, 'past invoice'), res)
// })

const productPrice = catchAsync(async (req, res) => {
    const result = await paymentService.fetchProductPrice(req);
    if (result) {
        res.message = _localize('module.get', req, 'price');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const getSubscription = catchAsync(async (req, res) => {
    const result = await paymentService.getSubscription(req);
    if (result) {
        res.message = _localize('module.get', req, 'Subscription');
        return util.successResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'Subscription');
    return util.recordNotFound(null, res);
})

const cancelSubscription = catchAsync(async (req, res) => {
    const result = await paymentService.cancelSubscription(req);
    if (result) {
        res.message = _localize('module.cancel', req, 'Subscription');
        return util.successResponse(result, res);
    }
    return util.failureResponse(
        _localize('module.cancelError', req, 'Subscription'),
        res,
    );
})

const unCancelSubscription = catchAsync(async (req, res) => {
    const result = await paymentService.uncancelSubscription(req);
    if (result) {
        res.message = _localize('subscription.uncancel', req, '');
        return util.successResponse(result, res);
    }
    return util.failureResponse(
        _localize('module.cancelError', req, 'Subscription'),
        res,
    );
})

const updateSubscription = catchAsync(async (req, res) => {
    const result = await paymentService.updateSubscription(req);
    
    if (result) {
        res.message = _localize('module.update', req, 'Subscription');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'Subscription'), res);
})

const updatePaymentMethod = catchAsync(async (req, res) => {
    const result = await paymentService.updatePaymentMethod(req);
    if (result) {
        res.message = _localize('module.update', req, 'Card Details');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'Card Details'), res);
})

const defaultPaymentMethod = catchAsync(async (req, res) => {
    const result = await paymentService.defaultPaymentMethod(req);
    if (result) {
        res.message = _localize('module.get', req, 'Default Payment Method');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);    
})

const cancelSubscriptionWebhook = catchAsync(async (req, res) => {
    const result = await paymentService.cancelSubscriptionWebhook(req);
    if (result) {
        res.message = _localize('subscription.cancelSubscrptionWebhook', req, '');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('subscription.cancelError', req, ''), res);
})

const getInvoiceList = catchAsync(async (req, res) => {
    const result = await paymentService.getInvoiceList(req);
    if (result) {
        res.message = _localize('module.list', req, 'Invoice');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const paymentForStorageRequest = catchAsync(async (req, res) => {
    const result = await paymentService.storageRequestCharge(req);
    if (result) {
        res.message = _localize('module.storageRequestAccept', req, '');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.storageRequestUpdateError', req, ''), res);
})

const invoicePaidWebhook = catchAsync(async (req, res) => {
    const result = await paymentService.invoicePaidWebhook(req);
    if (result) {
        res.message = _localize('module.invoicePaid', req, '');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.invoicePaidError', req, ''), res);
})

const checkCoupon = catchAsync(async (req, res) => {
    const result = await paymentService.checkCoupon(req);
    if (result) {
        res.message = _localize('subscription.checkCoupon', req, '');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const handlePayment3dSecure=catchAsync(async (req,res)=>{
    const result=await paymentService.handlePayment3dSecure(req);

    if (result) {
        res.message = _localize('module.create', req, 'Subscription');
        return util.createdDocumentResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'subscription'), res);
})

const getStripePlans = catchAsync(async (req, res) => {
    const result = await paymentService.fetchStripePlans(req);
    if (result) {
        res.message = _localize('module.get', req, 'Stripe Plans');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const confirmStorageCharge = catchAsync(async (req, res) => {
    const result = await paymentService.confirmStorageCharge(req);
    if (result) {
        res.message = _localize('module.storageRequestCharge', req, '');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

module.exports = {
    createCustomer,
    upcomingInvoice,
    productPrice,
    getSubscription,
    cancelSubscription,
    updateSubscription,
    updatePaymentMethod,
    defaultPaymentMethod,
    cancelSubscriptionWebhook,
    getInvoiceList,
    paymentForStorageRequest,
    invoicePaidWebhook,
    checkCoupon,
    unCancelSubscription,
    handlePayment3dSecure,
    getStripePlans,
    confirmStorageCharge
}