const { Router } = require('express');
const router = Router();
const replythreadController = require('../../controller/web/replythreadController');
const { replyInThreadKeys } = require('../../utils/validations/thread');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', validate(replyInThreadKeys), authentication,checkPromptLimit, replythreadController.sendMessage);
router.post('/list', authentication, checkPromptLimit, replythreadController.getReplayThreadList);

module.exports = router;