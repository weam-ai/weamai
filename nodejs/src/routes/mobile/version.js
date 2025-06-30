const express = require('express');
const router = express.Router();
const versionController = require('../../controller/mobile/versionController');
const { deviceBasicAuth } = require('../../middleware/apiBasicAuth');

router.get('/', deviceBasicAuth, versionController.getMobileVersion);

module.exports = router;