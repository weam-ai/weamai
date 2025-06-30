const Favourite = require('../models/favourite');
const dbService = require('../utils/dbService');

const addFavourite = async (req) => {
    try {
        return Favourite.findOneAndUpdate(
            { threadId: req.body.threadId, userId: req.userId },
            req.body,
            { new: true, upsert: true },
        );
    } catch (error) {
        handleError(error, 'Error - addFavourite');
    }
};

const removeFavourite = async (req) => {
    try {
        const check = await Favourite.findOne({ threadId: req.body.threadId, userId: req.userId });
        if (!check) {
            return false;
        }
        return Favourite.deleteOne({
            threadId: req.body.threadId,
            userId: req.userId,
        });
    } catch (error) {
        handleError(error, 'Error - removeFavourite');
    }
};

const viewFavourite = async (req) => {
    try {
        return Favourite.findById({ _id: req.params.id, userId: req.userId })
    } catch (error) {
        handleError(error, 'Error - viewFavourite');
    }
};

const getAll = async (req) => {
    try {
        return dbService.getAllDocuments(
            Favourite,
            req.body.query || {},
            req.body.options || {},
        );
    } catch (error) {
        handleError(error, 'Error - getAll');
    }
};

module.exports = {
    addFavourite,
    removeFavourite,
    viewFavourite,
    getAll,
};
