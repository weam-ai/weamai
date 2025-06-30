const express = require('express');
const router = express.Router();
const stateController = require('../../controller/admin/stateController');
const { stateCreateKeys, stateUpdateKeys, partialUpdateKeys } = require('../../utils/validations/common');
const { authentication, checkPermission } = require('../../middleware/authentication');

router.post('/create', validate(stateCreateKeys), authentication, checkPermission, stateController.addState).descriptor('state.create');
router.put('/update/:id', validate(stateUpdateKeys), authentication, checkPermission, stateController.updateState).descriptor('state.update');
router.get('/get/:id', authentication, checkPermission, stateController.viewState).descriptor('state.view');
router.delete('/delete/:id', authentication, checkPermission, stateController.deleteState).descriptor('state.delete');
router.post('/list', authentication, checkPermission, stateController.getAll).descriptor('state.list');
router.patch('/partial/:id', validate(partialUpdateKeys), authentication, checkPermission, stateController.partialUpdate).descriptor('state.partialupdate');

module.exports = router;