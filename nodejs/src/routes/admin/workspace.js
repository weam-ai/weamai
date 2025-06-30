const express = require('express');
const router = express.Router();
const workspaceController = require('../../controller/admin/workspaceController');
const { createWorkspaceKeys, updateWorkspaceKeys } = require('../../utils/validations/workspace');
const { partialUpdateKeys } = require('../../utils/validations/common');
const { authentication, checkPermission } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', validate(createWorkspaceKeys), authentication, checkPermission,checkPromptLimit, workspaceController.addWorkSpace).descriptor('workspace.create');
router.put('/update/:slug', validate(updateWorkspaceKeys), authentication, checkPermission,checkPromptLimit, workspaceController.updateWorkSpace).descriptor('workspace.update');
router.get('/get/:slug', authentication, checkPermission, workspaceController.getWorkSpace).descriptor('workspace.view');
router.delete('/delete/:slug', authentication, checkPermission, workspaceController.deleteWorkSpace).descriptor('workspace.delete');
router.post('/list', authentication, checkPermission, checkPromptLimit, workspaceController.getAllWorkSpace).descriptor('workspace.list');
router.patch('/partial/:slug"', validate(partialUpdateKeys), authentication, checkPermission, workspaceController.partialUpdate).descriptor('workspace.partial');

module.exports = router;