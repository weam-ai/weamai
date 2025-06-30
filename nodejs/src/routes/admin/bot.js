const express = require('express');
const router = express.Router();
const botController = require('../../controller/admin/botController');
const { addBotKeys, updateBotKeys } = require('../../utils/validations/bot');
const { partialUpdateKeys } = require('../../utils/validations/common');
const { authentication, checkPermission } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', validate(addBotKeys), authentication, checkPermission, botController.addBot).descriptor('bot.create');
router.put('/update/:id', validate(updateBotKeys), authentication, checkPermission, botController.updateBot).descriptor('bot.update');
router.get('/:id', authentication, checkPermission, botController.viewBot).descriptor('bot.view');
router.delete('/delete/:id', authentication, checkPermission, botController.deleteBot).descriptor('bot.delete');
router.post('/list', authentication, checkPermission, checkPromptLimit, botController.getAll).descriptor('bot.list');
router.patch('/partial/:id', validate(partialUpdateKeys), authentication, checkPermission, botController.partialUpdate).descriptor('bot.partialupdate');

module.exports = router;