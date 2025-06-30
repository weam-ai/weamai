const { Router } = require('express');
const router = Router();
const customgptController = require('../../controller/web/customgptController');
const { authentication } = require('../../middleware/authentication');
const { createCustomGptKeys, updateCustomGptKeys, assignDefaultGpt } = require('../../utils/validations/customgpt');
const { upload, checkAndUpdateStorage    } = require('../../middleware/multer');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', authentication, checkPromptLimit, upload.fields([{ name: 'doc', maxCount: 10 }, { name: 'coverImg', maxCount: 1 }]), checkAndUpdateStorage, validate(createCustomGptKeys), customgptController.addCustomGpt);
router.post('/assigngpt', validate(assignDefaultGpt), authentication,checkPromptLimit, customgptController.assignGpt);
router.put('/update/:id', authentication, checkPromptLimit, upload.fields([{ name: 'doc', maxCount: 10 }, { name: 'coverImg', maxCount: 1 }]), checkAndUpdateStorage, validate(updateCustomGptKeys), customgptController.updateCustomGpt);
router.get('/:id', authentication, customgptController.viewCustomGpt);
router.delete('/delete/:id', authentication, customgptController.deleteCustomGpt);
router.post('/list', authentication, checkPromptLimit, customgptController.getAll);
router.post('/user/getAll', authentication, customgptController.usersWiseGetAll);
router.put('/favorite/:id', authentication, customgptController.favoriteCustomGpt);

module.exports = router;
