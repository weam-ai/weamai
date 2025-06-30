const express = require('express');
const roleController = require('../../controller/web/roleController');
const router = express.Router();
const { authentication } = require('../../middleware/authentication');

router.post('/list', authentication, roleController.getAllRole)

module.exports = router;