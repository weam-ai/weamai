const Bookmark = require('../models/bookmark');
const dbService = require('../utils/dbService');

const addBookmark = async (req) => {
    try {
        return Bookmark.findOneAndUpdate(req.body, { new: true, upsert: true });
    } catch (error) {
        handleError(error, 'Error - addBookmark');
    }
}

const removeBookmark = async (req) => {
    try {
        return Bookmark.deleteOne(req.body);
    } catch (error) {
        handleError(error, 'Error - removeBookmark');
    }
}

module.exports = {
    addBookmark,
    removeBookmark,
};