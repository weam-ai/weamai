const paymentService = require('../../services/payment');
const subscriptionSSE = require('../../services/subscriptionSSE');

// const createCharge = catchAsync(async (req, res) => {
//     const result = await paymentService.createCharge(req);
//     if (result) {
//         res.message = _localize('module.success', req, 'payment');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.failed', req, 'payment'),
//         res,
//     );
// });

// const createCard = catchAsync(async (req, res) => {
//     const result = await paymentService.createCard(req);
//     if (result) {
//         res.message = _localize('module.create', req, 'stripe card');
//         return util.createdDocumentResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.createError', req, 'stripe card'),
//         res,
//     );
// });

// const updateCard = catchAsync(async (req, res) => {
//     const result = await paymentService.updateCard(req);
//     if (result) {
//         res.message = _localize('module.update', req, 'stripe card');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.updateError', req, 'stripe card'),
//         res,
//     );
// });

// const deleteCard = catchAsync(async (req, res) => {
//     const result = await paymentService.deleteCard(req);
//     if (result) {
//         res.message = _localize('module.delete', req, 'stripe card');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.deleteError', req, 'stripe card'),
//         res,
//     );
// });

// const getAllCards = catchAsync(async (req, res) => {
//     const result = await paymentService.getAllCards(req);
//     if (result) {
//         res.message = _localize('module.list', req, 'stripe card');
//         return util.successResponse(result, res);
//     }
//     res.message = _localize('module.listError', req, 'stripe card');
//     return util.recordNotFound(null, res);
// });

// const createCheckoutSession = catchAsync(async (req, res) => {
//     const result = await paymentService.createCheckoutSession(req);
//     if (result) {
//         res.message = _localize('module.create', req, 'checkout session');
//         return util.createdDocumentResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.createError', req, 'checkout session'),
//         res,
//     );
// });

// const cancelSubscription = catchAsync(async (req, res) => {
//     const result = await paymentService.cancelSubscription(req);
//     if (result) {
//         res.message = _localize('module.cancel', req, 'subscription');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.cancelError', req, 'subscription'),
//         res,
//     );
// });

// const resumeSubscription = catchAsync(async (req, res) => {
//     const result = await paymentService.resumeSubscription(req);
//     if (result) {
//         res.message = _localize('module.update', req, 'subscription');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.updateError', req, 'subscription'),
//         res,
//     );
// });

// const createInvoice = catchAsync(async (req, res) => {
//     const result = await paymentService.createInvoice(req);
//     if (result) {
//         res.message = _localize('module.create', req, 'invoice');
//         return util.createdDocumentResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.createError', req, 'invoice'),
//         res,
//     );
// });

// const retrieveInvoice = catchAsync(async (req, res) => {
//     const result = await paymentService.retrieveInvoice(req);
//     if (result) {
//         res.message = _localize('module.get', req, 'invoice');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.getError', req, 'invoice'),
//         res,
//     );
// });

// const upcomingInvoice = catchAsync(async (req, res) => {
//     const result = await paymentService.upcomingInvoice(req);
//     if (result) {
//         res.message = _localize('module.get', req, 'upcoming invoice');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.getError', req, 'upcoming invoice'),
//         res,
//     );
// });

// const managePastInvoice = catchAsync(async (req, res) => {
//     const result = await paymentService.managePastInvoice(req);
//     if (result) {
//         res.message = _localize('module.list', req, 'past invoice');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(
//         _localize('module.listError', req, 'past invoice'),
//         res,
//     )
// })

// const transactionList = catchAsync(async (req, res) => {
//     const result = await paymentService.transactionList(req);
//     if (result) {
//         res.message = _localize('module.list', req, 'transaction');
//         return util.successResponse(result, res);
//     }
//     return util.failureResponse(_localize('module.listError', req, 'transaction'), res);
// })

const getSubscription = catchAsync(async (req, res) => {
    const result = await paymentService.getSubscription(req);
    if (result) {
        res.message = _localize('module.get', req, 'Subscription');
        return util.successResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'Subscription');
    return util.recordNotFound(null, res);
})


const subscriptionSSEEvent = catchAsync(async (req,res) => {
   return await subscriptionSSE.subscriptionSSEEvent(req,res);
})

module.exports = {
    // createCharge,
    // createCard,
    // updateCard,
    // deleteCard,
    // getAllCards,
    // createCheckoutSession,
    // resumeSubscription,
    // createInvoice,
    // retrieveInvoice,
    // retrieveInvoice,
    // upcomingInvoice,
    // managePastInvoice,
    // transactionList,
    subscriptionSSEEvent,
    getSubscription    
};
