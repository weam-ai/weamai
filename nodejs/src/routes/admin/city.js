const express = require('express');
const router = express.Router();
const cityController = require('../../controller/admin/cityController');
const { cityCreateKeys, cityUpdateKeys, partialUpdateKeys } = require('../../utils/validations/common');
const { authentication, checkPermission } = require('../../middleware/authentication');

router.post('/create', validate(cityCreateKeys), authentication, checkPermission, cityController.addCity).descriptor('city.create');
router.put('/update/:id', validate(cityUpdateKeys), authentication, checkPermission, cityController.updateCity).descriptor('city.update');
router.get('/get/:id', authentication, checkPermission, cityController.viewCity).descriptor('city.view');
router.delete('/delete/:id', authentication, checkPermission, cityController.deleteCity).descriptor('city.delete');
router.post('/list', authentication, checkPermission, cityController.getAll).descriptor('city.list');
router.patch('/partial/:id', validate(partialUpdateKeys), authentication, checkPermission, cityController.partialUpdate).descriptor('city.partialupdate');

module.exports = router;