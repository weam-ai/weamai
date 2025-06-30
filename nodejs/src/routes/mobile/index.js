const express = require('express');

const router = express.Router();

router.use('/version', require('./version'));

module.exports = router;
