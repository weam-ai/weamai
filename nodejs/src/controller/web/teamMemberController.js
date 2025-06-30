const { catchAsync } = require("../../utils/helper");
const teamMemberService = require("../../services/teamMember");


const getAll = catchAsync(async (req, res) => {
  const result = await teamMemberService.getAll(req);

  if (result) {
    res.message = _localize("module.get", req, "team user");
    return util.successResponse(result, res);
  }
  return util.failureResponse(_localize("module.getError", req, "team user"), res);
});

const shareTeamList = catchAsync(async (req, res) => {
  const result = await teamMemberService.shareBrainList(req);

  if (result) {
    res.message = _localize("module.get", req, "team");
    return util.successResponse(result, res);
  }
  return util.failureResponse(_localize("module.getError", req, "team"), res);
});

const updateShareTeamToWorkspace = catchAsync(async (req, res) => {
  const result = await teamMemberService.updateShareTeamToWorkspace(req);

  if (result) {
    res.message = _localize("module.update", req, "workspace team");
    return util.successResponse(result, res);
  }
  return util.failureResponse(
    _localize("module.updateError", req, "workspace team"),
    res
  );
});

const deleteShareTeamToWorkspace = catchAsync(async (req, res) => {
  const result = await teamMemberService.deleteShareTeamToWorkspace(req);

  if (result) {
    res.message = _localize("module.delete", req, "workspace team");
    return util.successResponse(result, res);
  }
  return util.failureResponse(
    _localize("module.deleteError", req, "workspace team"),
    res
  );
});


const updateShareTeam = catchAsync(async (req, res) => {
  const result = await teamMemberService.updateShareTeamToBrain(req);

  if (result) {
    res.message = _localize("module.update", req, "brain team");
    return util.successResponse(result, res);
  }
  return util.failureResponse(
    _localize("module.updateError", req, "brain team"),
    res
  );
});

const deleteShareTeamToBrain = catchAsync(async (req, res) => {
  const result = await teamMemberService.deleteShareTeamToBrain(req);

  if (result) {
    res.message = _localize("module.delete", req, "brain team");
    return util.successResponse(result, res);
  }
  return util.failureResponse(
    _localize("module.deleteError", req, "workspace team"),
    res
  );
});

const deleteShareTeamToChat=catchAsync(async(req,res)=>{

  
    const result = await teamMemberService.deleteShareTeamToChat(req);
  
    if (result) {
      res.message = _localize("module.delete", req, "chat team");
      return util.successResponse(result, res);
    }
    return util.failureResponse(
      _localize("module.deleteError", req, "chat team"),
      res
    );
  })

  module.exports = {
    getAll,
    shareTeamList,
    updateShareTeamToWorkspace,
    deleteShareTeamToWorkspace,
    updateShareTeam,
    deleteShareTeamToBrain,
    deleteShareTeamToChat
  };
  