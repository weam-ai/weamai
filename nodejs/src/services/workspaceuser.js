const dbService = require('../utils/dbService');
const WorkspaceUser = require('../models/workspaceuser');
const Workspace = require('../models/workspace');
const { addWorkSpaceUsers } = require('./workspace');
const { accessOfWorkspaceToUser } = require('./common');
const ShareBrain =require("../models/shareBrain");
const { removeBrainChatMember } = require('./chatmember');
const Brain = require("../models/brains");
const { defaultGeneralBrainMember } = require('./brain');
const { DEFAULT_NAME } = require('../config/constants/common');
const getAllWorkSpaceUser = async (req) => {
    try {
        return dbService.getAllDocuments(WorkspaceUser, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error - getAllWorkSpaceUser');
    }
}

const addWorkSpaceUser = async (req) => {
    try {
        const { users, workspaceId } = req.body;

        const  accessOfWorkspace = await accessOfWorkspaceToUser({workspaceId , userId : req.user.id})
        
        if(!accessOfWorkspace){  
            throw new Error(_localize('module.unAuthorized', req,'Workspace'))
        }

        const findWorkspace = await Workspace.findById({ _id: workspaceId });
        
        // Add users to general brain
        const generalBrain = await Brain.findOne({ 
            workspaceId, 
            'title': DEFAULT_NAME.GENERAL_BRAIN_TITLE
        });

        if (generalBrain) {
            const shareBrainPromises = users.map(user => {
                defaultGeneralBrainMember(req,findWorkspace._id, { ...user, _id:user.id, company: req.user.company, invitedBy: req.user?.invitedBy });
            });
            await Promise.all(shareBrainPromises);
        }
        
        return addWorkSpaceUsers(users, findWorkspace, req.user);
    } catch (error) {
        handleError(error, 'Error - addWorkSpaceUser');
    }
}

const deleteWorkSpaceUser = async (req) => {
    try {

        const  accessOfWorkspace = await accessOfWorkspaceToUser({workspaceId:req.params.id , userId : req.user.id})
        
        if(!accessOfWorkspace){  
            throw new Error(_localize('module.unAuthorized', req,'Workspace'))
        }

        const brainIds = req.body.sharedBrains?.map((curr) => curr._id);

         
         await ShareBrain.deleteMany({ "brain.id": { $in: brainIds }, 'user.id': req.body.user_id,teamId:{$exists:false} });
     

        for (const currBrainId of brainIds) {
            await removeBrainChatMember(currBrainId, req.body.user_id);
        }
        

        return WorkspaceUser.deleteOne({ workspaceId: req.params.id, 'user.id': req.body.user_id,teamId:{$exists:false }})
    } catch (error) {
        handleError(error, 'Error - deleteWorkSpaceUser');
    }
}

module.exports = {
    getAllWorkSpaceUser,
    addWorkSpaceUser,
    deleteWorkSpaceUser
}