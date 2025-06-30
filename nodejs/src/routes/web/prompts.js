const express = require('express');
const router = express.Router();
const promptController = require('../../controller/web/promptController');
const { createPromptKeys, editPromptKeys } = require('../../utils/validations/prompts');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', validate(createPromptKeys), authentication, checkPromptLimit, promptController.addPrompt);
router.post('/list', authentication, checkPromptLimit, promptController.getPromptList);
router.delete('/delete/:id', authentication, promptController.deletePrompt);
router.put('/update/:id', validate(editPromptKeys), authentication, checkPromptLimit, promptController.updatePrompt);
router.post('/user/getAll', authentication, promptController.usersWiseGetAll);
router.put('/favorite/:id', authentication, promptController.favoritePrompt);

module.exports = router;