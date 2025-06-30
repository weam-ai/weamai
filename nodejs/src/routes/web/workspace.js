const express = require('express');
const router = express.Router();
const workspaceController = require('../../controller/admin/workspaceController');
const { createWorkspaceKeys, updateWorkspaceKeys } = require('../../utils/validations/workspace');
const { partialUpdateKeys } = require('../../utils/validations/common');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', validate(createWorkspaceKeys), authentication,checkPromptLimit, workspaceController.addWorkSpace);
router.put('/update/:slug', validate(updateWorkspaceKeys), authentication,checkPromptLimit, workspaceController.updateWorkSpace);
router.get('/get/:slug', authentication, workspaceController.getWorkSpace);
router.delete('/delete/:slug', authentication, workspaceController.deleteWorkSpace);
router.delete('/deleteall', authentication, workspaceController.deleteAllWorkSpace);
router.post('/list', authentication, checkPromptLimit, workspaceController.getAllWorkSpace);
router.patch('/partial/:slug"', validate(partialUpdateKeys), authentication, workspaceController.partialUpdate);
router.post('/restore/:slug', authentication, workspaceController.restoreWorkspace);

module.exports = router;