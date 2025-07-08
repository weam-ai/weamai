// getAllStorageRequest
const express = require('express');
const router = express.Router();
const storageRequestController = require('../../controller/admin/storageRequestController');
const { authentication, checkPermission } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/list', authentication, checkPermission,checkPromptLimit, storageRequestController.getAllStorageRequest).descriptor('storagerequest.list');
router.post('/decline', authentication, checkPermission, storageRequestController.declineStorageRequest).descriptor('storagerequest.decline');
router.post('/approve', authentication, checkPermission, storageRequestController.approveStorageRequest).descriptor('storagerequest.approve');

module.exports = router;