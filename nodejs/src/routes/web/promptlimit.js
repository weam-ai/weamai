const express = require('express');
const router = express.Router();
const promptLimitController = require('../../controller/web/promptLimitController');
const { setPromptLimitKeys } = require('../../utils/validations/common');
const { authentication } = require('../../middleware/authentication');

router.put('/set/:id', validate(setPromptLimitKeys), authentication, promptLimitController.setPromptLimit);

module.exports = router;