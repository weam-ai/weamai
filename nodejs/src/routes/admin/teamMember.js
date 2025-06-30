const { Router } = require("express");
const {
    authentication,
    checkPermission,
} = require("../../middleware/authentication");
const { checkPromptLimit } = require('../../middleware/promptlimit');
const teamMemberRouter = Router();
const teamMemberController = require("../../controller/admin/teamMemberController");

teamMemberRouter
    .post(
        "/create",
        authentication,
        checkPermission,
        checkPromptLimit,
        teamMemberController.addTeam
    )
    .descriptor("team.create");

teamMemberRouter
    .put(
        "/update/:id",
        authentication,
        checkPermission,
        checkPromptLimit,
        teamMemberController.updateTeam
    )
    .descriptor("team.update");
teamMemberRouter
    .delete(
        "/delete/:id",
        authentication,
        checkPermission,
        teamMemberController.deleteTeam
    )
    .descriptor("team.delete");

module.exports = teamMemberRouter;
