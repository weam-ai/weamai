const { Router } = require('express');
const workSpaceUserController = require('../../controller/web/workspaceuserController');
const { authentication } = require('../../middleware/authentication');
const router = Router();
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/list', authentication, checkPromptLimit, workSpaceUserController.getAllWorkSpaceUser);

module.exports = router;