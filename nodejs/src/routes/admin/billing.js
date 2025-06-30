const express = require('express');
const billingController = require('../../controller/admin/billingController');
const { authentication, checkPermission } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');
const router = express.Router();

router.post('/list', authentication, checkPermission, checkPromptLimit,  billingController.getAllMembers).descriptor('billing.list');

module.exports = router;