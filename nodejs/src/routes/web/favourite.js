const { Router } = require('express');
const router = Router();
const favouriteController = require('../../controller/web/favouriteController');
const { addFavouriteKeys, removeFavouriteKeys } = require('../../utils/validations/favourite');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/add', validate(addFavouriteKeys), authentication, favouriteController.addFavourite);
router.delete('/remove', validate(removeFavouriteKeys), authentication, favouriteController.removeFavourite);
router.get('/get/:id', authentication, favouriteController.viewFavourite);
router.post('/list', authentication, checkPromptLimit, favouriteController.getAll);

module.exports = router;