const express = require('express');
const { authentication } = require('../../middleware/authentication');
const creditControlController = require('../../controller/admin/creditControlController');
const router =express.Router()

router.post('/add-credit', authentication, creditControlController.addCreditById).descriptor('creditControl.addCreditById');

module.exports = router;