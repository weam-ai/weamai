const express = require('express');
const router = express.Router();
const workspaceuserController = require('../../controller/admin/workspaceuserController');
const { authentication, checkPermission } = require('../../middleware/authentication');
const { addWorkSpaceUserKeys, deleteWorkSpaceUserKeys } = require('../../utils/validations/workspace');
const { checkPromptLimit } = require('../../middleware/promptlimit');
router.post('/create', validate(addWorkSpaceUserKeys), authentication,checkPromptLimit, checkPermission, workspaceuserController.addWorkSpaceUser).descriptor('workspaceuser.create');
router.post('/list', authentication, checkPermission, checkPromptLimit, workspaceuserController.getAllWorkSpaceUser).descriptor('workspaceuser.list');
router.delete('/delete/:id', validate(deleteWorkSpaceUserKeys), authentication, checkPermission, workspaceuserController.deleteWorkSpaceUser).descriptor('workspaceuser.delete');

module.exports = router;