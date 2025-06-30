const { Router } = require('express');
const router = Router();
const chatMemberController = require('../../controller/web/chatMemberController');
const { addChatMemberKeys, favouriteKeys } = require('../../utils/validations/chat');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', validate(addChatMemberKeys), authentication, chatMemberController.addChatMember);
router.delete('/delete/:id', authentication, chatMemberController.removeChatMember);
router.post('/list', authentication, checkPromptLimit, chatMemberController.memberList);
router.put('/partial/:id', validate(favouriteKeys), authentication, chatMemberController.favouriteChat);

module.exports = router;