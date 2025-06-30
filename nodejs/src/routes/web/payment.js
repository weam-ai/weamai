const express = require('express');
const router = express.Router();
const paymentController = require('../../controller/web/paymentController');
const {
    createCardKeys,
    createCustomerKeys,
    updateCardKeys,
    deleteCardKeys,
    createChargesKeys,
    checkoutSessionKeys,
    cancelSubscriptionKeys,
    resumeSubscriptionKeys,
    paymentIntent,
} = require('../../utils/validations/payment');
const { authentication, checkPermission } = require('../../middleware/authentication');

// router.post(
//     '/add-card',
//     validate(createCardKeys),
//     authentication,
//     paymentController.createCard,
// );
// router.post(
//     '/create-charge',
//     validate(createChargesKeys),
//     authentication,
//     paymentController.createCharge,
// );
// router.post(
//     '/update-card',
//     validate(updateCardKeys),
//     authentication,
//     paymentController.updateCard,
// );
// router.post(
//     '/remove-card',
//     validate(deleteCardKeys),
//     authentication,
//     paymentController.deleteCard,
// );
// router.get('/view-cards/:id', authentication, paymentController.getAllCards);
// router.post(
//     '/checkout-session',
//     validate(checkoutSessionKeys),
//     // authentication,
//     paymentController.createCheckoutSession,
// );
// router.delete(
//     '/cancel-subscription',
//     validate(cancelSubscriptionKeys),
//     authentication,
//     paymentController.cancelSubscription,
// );
//     router.post(
//         '/resume-subscription',
//         validate(resumeSubscriptionKeys),
//         authentication,
//         paymentController.resumeSubscription,
// );
// router.post('/create-invoice', authentication, paymentController.createInvoice);
// router.get(
//     '/get-invoice/:id',
//     authentication,
//     paymentController.retrieveInvoice,
// );
// router.get(
//     '/upcoming-invoice',
//     authentication,
//     paymentController.upcomingInvoice,
// );
// router.get('/manage-pastinvoice', authentication, paymentController.managePastInvoice);
// router.get('/transaction-list', authentication, checkPermission, paymentController.transactionList);

router.get('/get-subscription', authentication, paymentController.getSubscription)
router.get('/sse/subscriptionEvent', authentication, paymentController.subscriptionSSEEvent);
module.exports = router;
