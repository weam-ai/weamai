const { SHARE_CHAT_TYPE } = require('../config/constants/common');
const ShareChat = require('../models/shareChat');
const dbService = require('../utils/dbService');

const createShareChat = async (req) => {
    try {
        return ShareChat.findOneAndUpdate(
            { chatId: req.body.chatId },  
            { ...req.body, permission: SHARE_CHAT_TYPE.READ_ONLY, shareBy: req.userId },
            { new: true, upsert: true }
        );
    } catch (error) {
        handleError(error, 'Error - createShareChat');
    }
}

const getAllShareChat = async (req) => {
    try {
        const { query = {}, options = {} } = req.body || {};
        return dbService.getAllDocuments(ShareChat, query, options);
    } catch (error) {
        handleError(error, 'Error - getAllShareChat');
    }
}

const deleteShareChats = async (req) => {
    try {
        const filter = { shareBy: req.userId };
        if (req.body.isBulk) {
            return ShareChat.deleteMany(filter)
        }
        filter['_id'] = req.body.id;
        return ShareChat.deleteOne(filter);
    } catch (error) {
        handleError(error, 'Error - deleteShareChats');
    }
}

const viewShareChat = async (req) => {
    try {
        return ShareChat.findOne({ chatId: req.params.id });
    } catch (error) {
        handleError(error, 'Error - viewShareChat');
    }
}



module.exports = {
    createShareChat,
    getAllShareChat,
    deleteShareChats,
    viewShareChat
}