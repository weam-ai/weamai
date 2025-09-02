const { Router } = require('express');
const router = Router();
const solutionInstallProgressController = require('../../controller/web/solutionInstallProgressController');

router.get('/progress', solutionInstallProgressController.getInstallationProgress);

module.exports = router;
