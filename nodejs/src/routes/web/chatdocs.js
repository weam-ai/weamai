const { Router } = require('express');
const chatDocController = require('../../controller/web/chatDocController');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');
const router = Router();

router.post('/list', authentication, checkPromptLimit, chatDocController.getAllChatDocs);
router.delete('/delete/:id', authentication, chatDocController.deleteChatDoc);
router.post('/user/getAll', authentication, chatDocController.usersWiseGetAll);
router.put('/favorite/:id', authentication, chatDocController.favoriteChatDoc);

module.exports = router;
