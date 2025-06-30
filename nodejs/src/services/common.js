const Chat = require('../models/chat');
const ChatMember = require('../models/chatmember');
const ShareBrain=require("../models/shareBrain")
const WorkSpaceUser=require("../models/workspaceuser")
const User = require('../models/user');
const Company = require('../models/company');

const addChatMemberTitle = async (req) => {
    try {
        const getAllChat = await Chat.find({ title: { $exists: true } }, { title: 1, _id: 1 });

        const bulkUpdates = [];

        for (const element of getAllChat) {
            const member = await ChatMember.find({ chatId: element._id }, { _id: 1 });

            if (member.length > 0) {
                bulkUpdates.push({
                    updateMany: {
                        filter: { chatId: element._id },
                        update: { $set: { title: element.title } }
                    }
                });
            }
        }

        if (bulkUpdates.length > 0) {
            await ChatMember.bulkWrite(bulkUpdates);
        }
        return true;
    } catch (error) {
        handleError(error, 'Error - addChatMemberTitle');
    }
}

const accessOfWorkspaceToUser = async ({workspaceId , userId , isPopulateWorkspace=false})=>{
    try {
        const query = WorkSpaceUser.findOne({ workspaceId: workspaceId, "user.id": userId });

        if (isPopulateWorkspace) {
            query.populate("workspaceId");
        }

        return await query
    } catch (error) {
        handleError(error, "accessOfWorkspace");
    }
}


const accessOfBrainToUser= async ({brainId,userId})=>{
    try {
        return await ShareBrain.findOne({"brain.id":brainId,"user.id":userId})
    } catch (error) {
        handleError(error, 'Error - accessOfBrainToUser');
    }
}

const updateCredit = async (req) => {
    try {
        return User.updateOne({ email: req.body.email }, { $inc: { msgCredit: req.body.credit } }, { new: true });
    } catch (error) {
        handleError(error, 'Error - updateCredit');
    }
}

const freeMessageCountMigration = async () => {
    try {
        const company = await Company.find({ queryLimit: { $exists: true } }, { usedFreeMessages: 1, queryLimit: 1 });
        if (company.length) {
            const bulkUpdates = [];
            if (bulkUpdates.length) {
                await Company.bulkWrite(bulkUpdates);
                return {
                    totalUpdated: bulkUpdates.length,
                    totalCompanies: company.length
                }
            }
        }
        return true;
    } catch (error) {
        handleError(error, 'Error - freeMessageCountMigration');
    }
}

module.exports = {
    addChatMemberTitle,
    accessOfWorkspaceToUser,
    accessOfBrainToUser,
    updateCredit,
    freeMessageCountMigration,
};
