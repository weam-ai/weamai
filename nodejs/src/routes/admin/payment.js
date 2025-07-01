const express = require('express');
const router = express.Router();
const paymentController = require('../../controller/admin/paymentController');
const { authentication, checkPermission, checkRole } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');
const { couponCodeKeys, createStripeCustomerKeys, storageRequestChargeKeys, updatePaymentMethodKeys, 
        updateSubscriptionKeys, cancelSubscriptionKeys } = require('../../utils/validations/subscription');

router.post('/create-customer', validate(createStripeCustomerKeys), authentication, checkPermission, 
    paymentController.createCustomer,
).descriptor('subscription.create-customer');
router.post('/payment-for-storage-request', validate(storageRequestChargeKeys), authentication, checkPermission, checkPromptLimit, paymentController.paymentForStorageRequest).descriptor('subscription.paymentforstoragerequest');

router.post('/uncancel-subscription', authentication, checkPermission, paymentController.unCancelSubscription).descriptor('subscription.uncancel');
router.post('/cancel-subscription', validate(cancelSubscriptionKeys), authentication, checkPermission, paymentController.cancelSubscription).descriptor('subscription.cancel');
router.post('/update-subscription', validate(updateSubscriptionKeys), authentication, checkPermission,
    paymentController.updateSubscription).descriptor('subscription.update');
router.post('/update-payment-method', validate(updatePaymentMethodKeys), authentication,checkPermission, paymentController.updatePaymentMethod).descriptor('subscription.paymentMethodupdate');

router.get('/default-payment-method',authentication,checkPermission,paymentController.defaultPaymentMethod).descriptor('subscription.defaultPaymentMethod');
router.get('/get-subscription', authentication, checkPermission, paymentController.getSubscription).descriptor('subscription.view');
//router.get('/get-product-price/:priceId', authentication, checkPermission, paymentController.productPrice).descriptor('subscription.plan');
router.get('/upcoming-invoice', authentication, checkPermission, paymentController.upcomingInvoice).descriptor('subscription.upcominginvoice');
router.post('/cancel-subscription-webhook', paymentController.cancelSubscriptionWebhook);
router.post('/invoice-list', authentication, checkPermission, paymentController.getInvoiceList).descriptor('payment.invoiceList');
router.post('/invoice-paid-webhook', paymentController.invoicePaidWebhook);
router.post('/check-coupon-code', validate(couponCodeKeys), authentication, paymentController.checkCoupon).descriptor('subscription.checkcouponcode');
router.post('/handle-payment-3dsecure',authentication,checkPermission,paymentController.handlePayment3dSecure).descriptor('subscription.handlePayment3dSecure')
router.get('/get-stripe-plans',authentication,checkPermission,paymentController.getStripePlans).descriptor('subscription.get-stripe-plans');
router.post('/confirm-storage-charge',authentication,checkPermission,paymentController.confirmStorageCharge).descriptor('subscription.confirmStorageCharge');

module.exports = router;