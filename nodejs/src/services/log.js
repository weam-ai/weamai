const Log = require('../models/log');
const dbService = require('../utils/dbService');

const activityLogList = async (req) => {
    try {
        return dbService.getAllDocuments(
            Log,
            req.body.query || {},
            req.body.options || {},
        )
    } catch (error) {
        handleError(error, 'Error - activityLogList')
    }
}

module.exports = {
    activityLogList
}