const { Router } = require('express');
const router = Router();
const userController = require('../../controller/web/userController');
const { storageRequestKeys } = require('../../utils/validations/user');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');
router.get('/storage/details', authentication, userController.storageDetails);
router.post('/storage/increase', validate(storageRequestKeys), authentication, checkPromptLimit , userController.storageIncrease);
router.get('/:id', authentication, userController.getUser)
router.post('/favorite-list', authentication, userController.userFavoriteList);
module.exports = router;