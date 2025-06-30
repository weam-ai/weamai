const razorpayPaymentService = require('../../services/razorpayPayment');

const createOrder = catchAsync( async (req, res) => {
    const result = await razorpayPaymentService.createRazorpayOrder(req);
    if (result) {
        res.message = _localize('module.create', req, 'Order');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const createSubscription = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.createSubscription(req);
    if (result) {
        res.message = _localize('module.create', req, 'Subscription');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const fetchSubscriptionPlan = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.fetchSubscriptionPlan(req);
    if (result) {
        res.message = _localize('module.get', req, 'Subscription Plan');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const verifySubscriptionPayment = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.verifySubscriptionPayment(req);
    if (result) {
        res.message = _localize('module.get', req, 'Subscription Payment');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const getRazorpaySubscription = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.getRazorpaySubscription(req);
    if (result) {
        res.message = _localize('module.get', req, 'Subscription');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const updateSubscription = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.updateSubscription(req);
    if (result) {
        res.message = _localize('module.update', req, 'Subscription');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const cancelSubscription = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.cancelSubscription(req);
    if (result) {
        res.message = _localize('module.update', req, 'Subscription');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const capturePaymentWebhook = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.capturePaymentWebhook(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const invoicePaidWebhook = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.invoicePaidWebhook(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const subscriptionActivityWebhook = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.subscriptionActivityWebhook(req, res);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const getRazorpayInvoiceList = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.getRazorpayInvoiceList(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const uncancelSubscription = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.uncancelSubscription(req);
    if (result) {
        res.message = _localize('module.update', req, 'Subscription');
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const getPaymentMethods = catchAsync(async (req, res) => {
    
    const result = await razorpayPaymentService.getPaymentMethods(req);
    if (result) {
        return util.successResponse(result, res);
    }
})

const updatePaymentMethod = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.updatePaymentMethod(req);
    if (result) {
        return util.successResponse(result, res);
    }
})

const storageRequestCharge = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.storageRequestCharge(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})  

const getStoragePrice = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.getStoragePrice(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const verifyStoragePayment = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.verifyStoragePayment(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const createRazorpayCustomer = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.createRazorpayCustomer(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const fetchRazorpayToken = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.fetchRazorpayToken(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const createRazorpayRecurringPayment = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.createRazorpayRecurringPayment(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const updateSubscriptionDemo = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.updateSubscriptionDemo(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const createSubscriptionPlan = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.createSubscriptionPlan(req);
    if (result) {
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const createVerificationOrder = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.createVerificationOrder(req);
    if (result) {
        res.message = 'Card verification order created successfully';
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

const verifyAndRefund = catchAsync(async (req, res) => {
    const result = await razorpayPaymentService.verifyAndRefund(req);
    if (result) {
        res.message = 'Card verified and amount refunded successfully';
        return util.successResponse(result, res);
    }
    return util.recordNotFound(null, res);
})

module.exports = {
    createSubscription,
    createOrder,
    fetchSubscriptionPlan,
    verifySubscriptionPayment,
    getRazorpaySubscription,
    updateSubscription,
    cancelSubscription,
    capturePaymentWebhook,
    getRazorpayInvoiceList,
    invoicePaidWebhook,
    uncancelSubscription,
    subscriptionActivityWebhook,
    getPaymentMethods,
    updatePaymentMethod,
    storageRequestCharge,
    getStoragePrice,
    verifyStoragePayment,
    createRazorpayCustomer,
    fetchRazorpayToken,
    createRazorpayRecurringPayment,
    updateSubscriptionDemo,
    createSubscriptionPlan,
    createVerificationOrder,
    verifyAndRefund
}   