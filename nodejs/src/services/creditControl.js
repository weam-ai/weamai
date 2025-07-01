const User = require('../models/user');
const Log = require('../models/log');
const { LOG_TYPE } = require('../config/constants/common');

const addCreditById = async (req) => {
    try {
        const { ids, credit, email } = req.body;
        const { company, email:loginEmail } = req.user;
        if (!ids || !Array.isArray(ids) || ids.length === 0) {
            return false;
        }
        let bulkUpdate = [];
        let bulkLogCreate = [];

        bulkUpdate = ids.map((id) => ({
            updateOne: {
                filter: { _id: id, 'company.id': company.id },
                update: { $inc: { msgCredit: credit } },
            },
        }));

        bulkLogCreate = email.map((email) => ({
            insertOne: {
                document: {
                    type: credit > 0 ? LOG_TYPE.ALLOCATE_CREDIT : LOG_TYPE.DEALLOCATE_CREDIT,
                    status: 'active',
                    data: {

                        emailFrom: loginEmail,
                        emailTo: email,
                        credit,
                        companyId: company.id,
                        message: credit > 0 ? `Allocated ${credit} credit to ${email} by ${loginEmail}` : `Removed ${credit} credit from ${email} by ${loginEmail}`,
                    },
                },
            },
        }));
        await Promise.all([
            User.bulkWrite(bulkUpdate),
            Log.bulkWrite(bulkLogCreate),
        ]);

        return true;
    } catch (error) {
        handleError(error, 'Error - addCreditById');
    }
};

const getCreditLogMessage = async () => {
    try {
        
        return await Log.find({
            type: { $in: [LOG_TYPE.ALLOCATE_CREDIT, LOG_TYPE.DEALLOCATE_CREDIT] },
        });

        
    } catch (error) {
        handleError(error, 'Error - getCreditLogMessage');
    }
}

module.exports = {
    addCreditById,
    getCreditLogMessage
};