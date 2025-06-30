const { Router } = require('express');
const brainController = require('../../controller/web/brainController');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');
const router = Router();

router.post('/list', authentication, checkPromptLimit, brainController.getAllBrainUser);

module.exports = router;