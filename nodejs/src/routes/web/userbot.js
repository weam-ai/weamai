const express = require('express');
const router = express.Router();
const { createUserBotKeys, updateUserBotKeys, viewApiKeys, removeUserBotKeys } = require('../../utils/validations/bot');
const userBotController = require('../../controller/web/userBotController');
const { partialUpdateKeys } = require('../../utils/validations/common');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');
router.post('/create', validate(createUserBotKeys), userBotController.addUserBot);
router.put('/update/:id', validate(updateUserBotKeys), authentication, userBotController.updateUserBot);
router.get('/:id', authentication, userBotController.viewUserBot);
router.delete('/remove', validate(removeUserBotKeys), authentication, userBotController.deleteUserBot);
router.patch('/partial/:id', authentication, validate(partialUpdateKeys), userBotController.partialUpdate);
router.post('/list', authentication, checkPromptLimit, userBotController.getAll);
router.post('/view-key', validate(viewApiKeys), authentication, userBotController.viewApiKey);

module.exports = router;