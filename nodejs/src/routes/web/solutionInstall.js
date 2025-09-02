const { Router } = require('express');
const router = Router();
const solutionInstallController = require('../../controller/web/solutionInstallController');
const { authentication } = require('../../middleware/authentication');

router.post('/', authentication, solutionInstallController.install);

module.exports = router;