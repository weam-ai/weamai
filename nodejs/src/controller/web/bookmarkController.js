const bookmarkService = require('../../services/bookmark');
// const { handleError } = require('../../utils/dbService');
// const util = require('../../utils/util');
// const _localize = require('../../utils/localize');
// const catchAsync = require('../../utils/catchAsync');  

const addBookmark = catchAsync(async (req, res) => {
    try {
        const result = await bookmarkService.addBookmark(req);
        if (result) {
            res.message = _localize('module.create', req, 'bookmark');
            return util.createdDocumentResponse(result, res);
        }
    } catch (error) {
        handleError(error, 'Error - addBookmark');
    }
})

const removeBookmark = catchAsync(async (req, res) => {
    try {
        const result = await bookmarkService.removeBookmark(req);
        if (result) {
            res.message = _localize('module.delete', req, 'bookmark');
            return util.deletedDocumentResponse(result, res);
        }
    } catch (error) {
        handleError(error, 'Error - removeBookmark');
    }
})

module.exports = {
    addBookmark,
    removeBookmark,
};