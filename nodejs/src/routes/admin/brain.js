const { Router } = require('express');
const router = Router();
const brainController = require('../../controller/admin/brainController');
const { createBrainKeys, updateBrainKeys, deleteBrainKeys, shareBrainKeys, unshareBrainKeys } = require('../../utils/validations/brain');
const { partialUpdateKeys } = require('../../utils/validations/common');
const { authentication } = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

router.post('/create', validate(createBrainKeys), authentication,checkPromptLimit, brainController.createBrain);
router.put('/update/:id', validate(updateBrainKeys), authentication,checkPromptLimit, brainController.updateBrain);
router.get('/:slug', authentication, brainController.getBrain);
router.delete('/delete/:id', validate(deleteBrainKeys), authentication, brainController.deleteBrain);
router.post('/list', authentication, checkPromptLimit, brainController.getAll);
router.patch('/partial/:slug', validate(partialUpdateKeys), authentication, brainController.partialUpdate);
router.delete('/unshare/:id', validate(unshareBrainKeys), authentication, brainController.unShareBrain);
router.post('/share/list', authentication, checkPromptLimit, brainController.shareList);

module.exports = router;