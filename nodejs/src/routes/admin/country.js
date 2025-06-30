const express = require('express');
const router = express.Router();
const countryController = require('../../controller/admin/countryController');
const { countryCreateKeys, countryUpdateKeys, partialUpdateKeys } = require('../../utils/validations/common');
const { authentication, checkPermission } = require('../../middleware/authentication');

router.post('/create', validate(countryCreateKeys), authentication, checkPermission, countryController.addCountry).descriptor('country.create');
router.put('/update/:id', validate(countryUpdateKeys), authentication, checkPermission, countryController.updateCountry).descriptor('country.update');
router.get('/get/:id', authentication, checkPermission, countryController.viewCountry).descriptor('country.view');
router.delete('/delete/:id', authentication, checkPermission, countryController.deleteCountry).descriptor('country.delete');
router.post('/list', authentication, checkPermission, countryController.getAll).descriptor('country.list');
router.patch('/partial/:id', validate(partialUpdateKeys), authentication, checkPermission, countryController.partialUpdate).descriptor('country.partialupdate');

module.exports = router;