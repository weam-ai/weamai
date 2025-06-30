const express = require('express');
const router = express.Router();
const notificationController = require('../../controller/web/notificationController');
const { authentication } = require('../../middleware/authentication');
const { manualNotificationKeys } = require('../../utils/validations/common');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/save-device/token', authentication, notificationController.saveToken);
router.put('/read', authentication, notificationController.updateReadStatus);
router.post('/list', authentication, checkPromptLimit, notificationController.getAll);
router.get('/count', authentication, notificationController.notificationCount);
router.post('/send', validate(manualNotificationKeys), notificationController.sendManualPushNotification);
router.delete('/delete', authentication, notificationController.deleteAll);

module.exports = router;