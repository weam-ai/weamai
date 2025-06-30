const express = require('express');
const router = express.Router();
const dashboardController = require('../../controller/admin/dashboardController');
const brainController = require('../../controller/web/brainController');
const { authentication } = require('../../middleware/authentication');

router.post('/company-usage', authentication, dashboardController.getCompanyUsage);

module.exports = router;
