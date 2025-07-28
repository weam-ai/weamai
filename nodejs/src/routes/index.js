const express = require('express');

const router = express.Router();

router.use('/admin', csrfMiddleware, require('./admin'));
router.use('/web', csrfMiddleware, require('./web'));
router.use('/upload', csrfMiddleware, require('./upload'));
router.use('/common', require('./common'));
router.use('/device', csrfMiddleware, require('./mobile'));

module.exports = router;