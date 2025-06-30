const { Router } = require("express");
const { authentication } = require("../../middleware/authentication");
const teamMemberRouter = Router();
const teamMemberController = require("../../controller/web/teamMemberController");
const { checkPromptLimit } = require('../../middleware/promptlimit');

teamMemberRouter.post("/list", authentication, checkPromptLimit, teamMemberController.getAll);

module.exports = teamMemberRouter;
