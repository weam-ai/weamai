const dbService = require('../utils/dbService');
const User = require('../models/user');
const ShareBrain = require('../models/shareBrain');
const WorkSpaceUser = require('../models/workspaceuser');
const ChatMember = require('../models/chatmember');
const { handleError } = require('../utils/helper');

const getAllMembers = async (req) => {
    try {
        const { query = {}, options = {} } = req.body ?? {};
        let excludeIds = [];
        let includeIds = [];

        if (query?.brainId && query?.chatId) {
            const includesBrainMember = await ShareBrain.find(
                {
                    "brain.id": query.brainId,
                    ...(query.teamId && { teamId: { $exists: false } }),
                },
                { _id: 1, user: 1 }
            );
            includeIds = includeIds?.concat(includesBrainMember.map(br => br?.user?.id?.toString()));

            const existingBrainUser = await ChatMember.find(
                { chatId: query.chatId, ...(query.teamId && { teamId: { $exists: false } }), },
                { _id: 1, user: 1 }
            );

            excludeIds = excludeIds?.concat(existingBrainUser?.map(br => br?.user?.id?.toString()));
            delete query.brainId;
            delete query.chatId;
        }else if(query?.brainId && query?.workspaceId){

            const existingBrainUser = await ShareBrain.find(
                { 'brain.id': query.brainId, ...(query.teamId && { teamId: { $exists: false } }), },
                { _id: 1, user: 1 }
            );
            const existingWorkSpaceUser = await WorkSpaceUser.find(
                { workspaceId: query.workspaceId, ...(query.teamId && { teamId: { $exists: false } }), },
                { _id: 1, user: 1 }
            );
            includeIds = excludeIds?.concat(existingWorkSpaceUser?.map(br => br?.user?.id?.toString()));

            excludeIds = excludeIds?.concat(existingBrainUser?.map(br => br?.user?.id?.toString()));
            delete query.brainId;
            delete query.workspaceId;
        }else if(query?.workspaceId){

            const existingWorkSpaceUser = await WorkSpaceUser.find(
                { workspaceId: query.workspaceId, 'user.id': { $ne: req.userId }, ...(query.teamId && { teamId: { $exists: false } }), },
                { _id: 1, user: 1, role: 1 }
            );
            const filterData = existingWorkSpaceUser
                .map(wspace => wspace?.user?.id?.toString());

            // include field is identiyfy if
            // true - only get member who added in workspace 
            // false - only get member filter by not in workspace
            if(query.include){
                includeIds = includeIds.concat(filterData);
                delete query.include;
            }else{
                excludeIds = excludeIds.concat(filterData);
            }

            delete query.workspaceId;
        }

        if (excludeIds.length > 0) {
            query['_id'] = { $nin: excludeIds };
        }
        if (includeIds.length > 0) {
            query['_id'] = { $in: includeIds };
        }

        return dbService.getAllDocuments(User, query, options);
    } catch (error) {
        handleError(error, 'Error - getAllMembers');
    }
};


module.exports = {
    getAllMembers
}