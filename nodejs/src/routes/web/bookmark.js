const { Router } = require('express');
const router = Router();
const bookmarkController = require('../../controller/web/bookmarkController');
const { authentication } = require('../../middleware/authentication');

router.get('/add', bookmarkController.addBookmark);
router.delete('/remove', authentication, bookmarkController.removeBookmark);

module.exports = router;