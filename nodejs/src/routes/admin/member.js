const express = require('express');
const memberController = require('../../controller/admin/memberController');
const { authentication, checkPermission } = require('../../middleware/authentication');
const router = express.Router();

router.post('/list', authentication, memberController.getAllMembers);

module.exports = router;