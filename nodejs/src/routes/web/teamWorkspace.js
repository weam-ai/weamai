const { Router } = require("express");
const { authentication } = require("../../middleware/authentication");
const { checkPromptLimit } = require('../../middleware/promptlimit');
const teamMemberController = require("../../controller/web/teamMemberController");
const teamWorkspaceRouter = Router();

teamWorkspaceRouter.put(
    "/update/:id",
    authentication,
    checkPromptLimit,
    teamMemberController.updateShareTeamToWorkspace
);

teamWorkspaceRouter.delete(
    "/delete/:id",
    authentication,
    teamMemberController.deleteShareTeamToWorkspace
);

module.exports = teamWorkspaceRouter;
