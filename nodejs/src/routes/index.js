const express = require('express');

const router = express.Router();

router.use('/admin', require('./admin'));
router.use('/web', require('./web'));
router.use('/upload', require('./upload'));
router.use('/common', require('./common'));
router.use('/device', require('./mobile'));

module.exports = router;