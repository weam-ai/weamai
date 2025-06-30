const express = require('express');
const invoiceController = require('../../controller/admin/invoiceController');
const router = express.Router();
const { authentication, checkPermission } = require('../../middleware/authentication');

router.post('/list', authentication, checkPermission, invoiceController.getInvoice).descriptor('invoice.list');

module.exports = router;