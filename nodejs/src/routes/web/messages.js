const express = require('express');
const router = express.Router();
const threadController = require('../../controller/web/threadController');
const { createConversationKeys, editMsgKeys, addReactionKeys, saveResponseTimeKeys } = require('../../utils/validations/thread');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');
router.put('/update/:id', validate(editMsgKeys), threadController.editMessage);
router.post('/list', authentication, checkPromptLimit, threadController.getAll);
router.post('/add-reaction', validate(addReactionKeys), authentication, threadController.addReaction);
router.post('/send', validate(createConversationKeys), authentication, threadController.sendMessage)
router.post('/save-time', validate(saveResponseTimeKeys), authentication, threadController.saveTime);
router.get('/credit', authentication, threadController.getUserMsgCredit);
router.post('/global-search', authentication, checkPromptLimit, threadController.searchMessage);

module.exports = router;