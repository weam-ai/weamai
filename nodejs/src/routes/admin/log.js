const express = require('express');
const router = express.Router();
const logController = require('../../controller/admin/logController');
const { authentication, checkPermission } = require('../../middleware/authentication');

router.post('/list', authentication, checkPermission, logController.activityLogList).descriptor('log.list');

module.exports = router;