const { catchAsync } = require("../../utils/helper");
const teamMemberService = require("../../services/teamMember");

const addTeam = catchAsync(async (req, res) => {
    const result = await teamMemberService.addTeam(req);

    if (result) {
        res.message = _localize("module.create", req, "team");
        return util.successResponse(result, res);
    }
    return util.failureResponse(
        _localize("module.createError", req, "team"),
        res
    );
});

const updateTeam = catchAsync(async (req, res) => {
    const result = await teamMemberService.updateTeam(req);

    if (result) {
        res.message = _localize("module.update", req, "team");
        return util.successResponse(result, res);
    }
    return util.failureResponse(
        _localize("module.updateError", req, "team"),
        res
    );
});

const deleteTeam = catchAsync(async (req, res) => {
    const result = await teamMemberService.deleteTeam(req);

    if (result) {
        res.message = _localize("module.delete", req, "team");
        return util.successResponse(result, res);
    }
    return util.failureResponse(
        _localize("module.deleteError", req, "team"),
        res
    );
});

module.exports = {
    addTeam,
    updateTeam,
    deleteTeam,
};
