const { Router } = require("express");
const { authentication } = require("../../middleware/authentication");
const teamMemberController = require("../../controller/web/teamMemberController");
const { checkPromptLimit } = require('../../middleware/promptlimit');

const teamBrainRouter = Router();

//add team to brain
teamBrainRouter.put(
    "/update/:id",
    authentication,
    checkPromptLimit,
    teamMemberController.updateShareTeam
);

// list of added team to brain/workspace/chat
teamBrainRouter.post(
    "/list",
    authentication,
    checkPromptLimit,
    teamMemberController.shareTeamList
);

//delete the team from brain
teamBrainRouter.delete(
    "/delete/:id",
    authentication,
    teamMemberController.deleteShareTeamToBrain
);

//delete the team from chat
teamBrainRouter.delete(
    "/chat/delete/:id",
    authentication,
    teamMemberController.deleteShareTeamToChat
);

module.exports = teamBrainRouter;
