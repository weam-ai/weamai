const express = require('express');
const router = express.Router();
const chatlogController = require('../../controller/web/chatlogController');
const { updateChatKeys } = require('../../utils/validations/bot');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.put('/create', validate(updateChatKeys), authentication, chatlogController.updateChat);
router.get('/:id', authentication, chatlogController.viewChat);
router.delete('/:id', authentication, chatlogController.deleteChat);
router.post('/list', authentication, checkPromptLimit, chatlogController.getAll);

module.exports = router;