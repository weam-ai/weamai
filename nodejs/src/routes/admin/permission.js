const express = require('express');
const rolePermissionController = require('../../controller/admin/rolePermissionController');
const { updatePermissionKeys } = require('../../utils/validations/permission');
const { authentication, checkPermission } = require('../../middleware/authentication');
const router = express.Router();

router.get('/get/:id', authentication, checkPermission, rolePermissionController.getPermission).descriptor('permission.view');
router.put('/update', validate(updatePermissionKeys), authentication, checkPermission, rolePermissionController.updatePermission).descriptor('permission.update');
router.get('/list', authentication, checkPermission, rolePermissionController.getAll).descriptor('permission.list');
router.get('/by-role/:id', authentication, checkPermission, rolePermissionController.getByRole).descriptor('permission.getByRole');

module.exports = router;