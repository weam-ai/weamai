const express = require("express");
const router = express.Router();
const razorpayPaymentController = require("../../controller/admin/razorpayPaymentController");
const {
  authentication,
  checkPermission,
} = require("../../middleware/authentication");

router
  .post(
    "/create-order",
    authentication,
    checkPermission,
    razorpayPaymentController.createOrder
  )
  .descriptor("razorpay.create-order");

router
  .post(
    "/create-subscription",
    authentication,
    checkPermission,
    razorpayPaymentController.createSubscription
  )
  .descriptor("razorpay.create-subscription");

router
  .get(
    "/fetch-subscription-plan",
    authentication,
    checkPermission,
    razorpayPaymentController.fetchSubscriptionPlan
  )
  .descriptor("razorpay.fetch-subscription-plan");

router
  .post(
    "/verify-subscription-payment",
    authentication,
    checkPermission,
    razorpayPaymentController.verifySubscriptionPayment
  )
  .descriptor("razorpay.verify-subscription-payment");

router
  .get(
    "/get-subscription",
    authentication,
    checkPermission,
    razorpayPaymentController.getRazorpaySubscription
  )
  .descriptor("razorpay.get-razorpay-subscription");

router
  .post(
    "/update-subscription",
    authentication,
    checkPermission,
    razorpayPaymentController.updateSubscription
  )
  .descriptor("razorpay.update-subscription");

router
  .post(
    "/cancel-subscription",
    authentication,
    checkPermission,
    razorpayPaymentController.cancelSubscription
  )
  .descriptor("razorpay.cancel-subscription");

router
  .post(
    "/capture-payment-webhook",
    razorpayPaymentController.capturePaymentWebhook
  )
  .descriptor("razorpay.capture-payment-webhook");

router
  .get(
    "/get-invoice-list",
    authentication,
    checkPermission,
    razorpayPaymentController.getRazorpayInvoiceList
  )
  .descriptor("razorpay.get-razorpay-invoice-list");

router
  .post("/invoice-paid-webhook", razorpayPaymentController.invoicePaidWebhook)
  .descriptor("razorpay.invoice-paid-webhook");

router
  .post(
    "/subscription-activity",
    razorpayPaymentController.subscriptionActivityWebhook
  )
  .descriptor("razorpay.subscription-activity-webhook");

router
  .post(
    "/uncancel-subscription",
    authentication,
    checkPermission,
    razorpayPaymentController.uncancelSubscription
  )
  .descriptor("razorpay.uncancel-subscription");

router
  .get(
    "/get-payment-method",
    authentication,
    checkPermission,
    razorpayPaymentController.getPaymentMethods
  )
  .descriptor("razorpay.get-payment-method");

  router.post(
    "/update-razorpay-payment-method",
    authentication,
    checkPermission,
    razorpayPaymentController.updatePaymentMethod
  )
  .descriptor("razorpay.update-payment-method");

  router.post(
    "/storage-request-charge",
    authentication,
    checkPermission,
    razorpayPaymentController.storageRequestCharge
  )
  .descriptor("razorpay.storage-request-charge");

router
  .get(
    "/get-storage-price",
    authentication,
    checkPermission,
    razorpayPaymentController.getStoragePrice
  )
  .descriptor("razorpay.get-storage-price");

router
  .post(
    "/verify-storage-payment",
    authentication,
    checkPermission,
    razorpayPaymentController.verifyStoragePayment
  )
  .descriptor("razorpay.verify-storage-payment");

router
  .post(
    "/create-razorpay-customer",
    authentication,
    razorpayPaymentController.createRazorpayCustomer
  )
  .descriptor("razorpay.create-razorpay-customer");

router
  .post(
    "/fetch-razorpay-token",
    authentication,
    razorpayPaymentController.fetchRazorpayToken
  )
  .descriptor("razorpay.fetch-razorpay-token");

router
  .post(
    "/create-recurring-payment",
    authentication,
    razorpayPaymentController.createRazorpayRecurringPayment
  )
  .descriptor("razorpay.create-recurring-payment");

router
  .post(
    "/update-subscription-demo",
    authentication,
    razorpayPaymentController.updateSubscriptionDemo
  )
  .descriptor("razorpay.update-subscription-demo");

router
  .post(
    "/create-subscription-plan",
    razorpayPaymentController.createSubscriptionPlan
  )
  .descriptor("razorpay.create-subscription-plan");

router
  .post(
    "/create-verification-order",
    authentication,
    razorpayPaymentController.createVerificationOrder
  )
  .descriptor("razorpay.create-verification-order");

router
  .post(
    "/verify-and-refund",
    authentication,
    razorpayPaymentController.verifyAndRefund
  )
  .descriptor("razorpay.verify-and-refund");
  
module.exports = router;
