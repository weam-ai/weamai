const express = require('express');
const roleController = require('../../controller/admin/roleController');
const router = express.Router();
const { createRoleSchemaKeys, updateRoleSchemaKeys } = require('../../utils/validations/role');
const { partialUpdateKeys } = require('../../utils/validations/common');
const { authentication, checkPermission } = require('../../middleware/authentication');

router.post('/create', validate(createRoleSchemaKeys), authentication, checkPermission, roleController.addRole).descriptor('role.create');
router.put('/update/:id', validate(updateRoleSchemaKeys), authentication, checkPermission, roleController.updateRole).descriptor('role.update');
router.get('/get/:id', authentication, checkPermission, roleController.getRole).descriptor('role.view');
router.delete('/delete/:id', authentication, checkPermission, roleController.deleteRole).descriptor('role.delete');
router.post('/list', authentication, checkPermission, roleController.getAllRole).descriptor('role.list');
router.patch('/partial/:id', validate(partialUpdateKeys), authentication, checkPermission, roleController.partialUpdate).descriptor('role.partialupdate');


module.exports = router;