const express = require('express');
const shareChatController = require('../../controller/web/shareChatController');
const router = express.Router();
const { authentication } = require('../../middleware/authentication');
const { createShareChatKeys, deleteShareChatKeys } = require('../../utils/validations/chat');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', validate(createShareChatKeys), authentication, shareChatController.createShareChat);
router.post('/list', authentication, checkPromptLimit, shareChatController.getAllShareChat);
router.get('/:id', shareChatController.viewShareChat);
router.delete('/delete', validate(deleteShareChatKeys), authentication, shareChatController.deleteShareChats);

module.exports = router;