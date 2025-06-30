const User = require('../models/user');
const WorkSpaceUser = require('../models/workspaceuser');
const ShareBrain = require('../models/shareBrain');
const dbService = require('../utils/dbService');

const getAllMembers = async (req) => {
    try {
        const { options = {}, query = {} } = req.body || {};

        const result = await dbService.getAllDocuments(User, query, options);

        const userIds = result.data.map(user => user._id);

        const totalWorkspacePromise = WorkSpaceUser.aggregate([
            { $match: { 'user.id': { $in: userIds } } },
            { $group: { _id: '$user.id', total: { $sum: 1 } } }
        ]);

        const totalBrainPromise = ShareBrain.aggregate([
            { $match: { 'user.id': { $in: userIds } } },
            { $group: { _id: '$user.id', total: { $sum: 1 } } }
        ]);

        const [workspaceCounts, brainCounts] = await Promise.all([totalWorkspacePromise, totalBrainPromise]);

        const workspaceCountMap = {};
        workspaceCounts.forEach(item => {
            workspaceCountMap[item._id] = item.total;
        });

        const brainCountMap = {};
        brainCounts.forEach(item => {
            brainCountMap[item._id] = item.total;
        });

        const finalResult = result.data.map(user => ({
            ...user._doc,
            totalWorkspace: workspaceCountMap[user._id] || 0,
            totalBrain: brainCountMap[user._id] || 0
        }));

        return {
            data: finalResult,
            paginator: result.paginator
        };
    } catch (error) {
        
    }
}

module.exports = {
    getAllMembers
}