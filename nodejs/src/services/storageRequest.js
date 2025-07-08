const StorageRequest = require('../models/storageRequest');
const dbService = require('../utils/dbService');
const { handleError } = require('../utils/helper');
const User = require('../models/user');
const { STORAGE_REQUEST_STATUS } = require('../config/constants/common');
const { EMAIL_TEMPLATE } = require('../config/constants/common');
const { sendSESMail } = require('./email');
const { getTemplate } = require('../utils/renderTemplate');
const { byteToMB } = require('../utils/helper');

const getAllStorageRequest = async (req) => {
    try {
        return dbService.getAllDocuments(StorageRequest, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error in storage request service get all');
    }
}

const checkStorageRequest = async (storageRequestId, status, companyId) => {
    try {
        const storageRequest = await dbService.getDocumentByQuery(StorageRequest, { 
            _id: storageRequestId,
            status: status,
            'company.id': companyId
        });
        return storageRequest;
    } catch (error) {
        handleError(error, `Error in storage request service check status`);
    }
}

const approveStorageRequest = async (req) => {
    try {
        const storageRequest = await dbService.findOneAndUpdateDocument(StorageRequest, 
            { _id: req.body.storageRequestId }, 
            { 
                status: STORAGE_REQUEST_STATUS.ACCEPT, 
                requestSize: req.body.updatedStorageSize 
            }
        );

        const userId = storageRequest.user.id;        
        const user = await User.findOneAndUpdate(
          { _id: userId },
          { $inc: { fileSize: req.body.updatedStorageSize }, $unset: { requestSize: 1 } }
        );

        const emailData = {
            name: user.fname + ' ' + user.lname,
            storageSize: req.body.updatedStorageSize / (1024 * 1024)
        }
        
        getTemplate(EMAIL_TEMPLATE.STORAGE_REQUEST_APPROVED, emailData).then(async (template) => {
            await sendSESMail(user.email, template.subject, template.body, attachments = [])
        })

        return storageRequest;
    } catch (error) {
        handleError(error, 'Error in storage request service update status');
    }
}

const declineStorageRequest = async (req) => {
    try {
        const storageRequest = await dbService.findOneAndUpdateDocument(StorageRequest, 
            { 
                _id: req.body.storageRequestId, 
                'company.id': req.user.company.id
            }, 
            { status: STORAGE_REQUEST_STATUS.DECLINE }
        );
        
        await User.findOneAndUpdate(
            { email: storageRequest.user.email },
            { $unset: { requestSize: 1 } }
        );

        return storageRequest;
    } catch (error) {
        handleError(error, 'Error in storage request service decline status');
    }
}

module.exports = {
    getAllStorageRequest,
    approveStorageRequest,
    checkStorageRequest,
    declineStorageRequest
}
