const creditControlService = require('../../services/creditControl');


const addCreditById = catchAsync(async (req, res) => {
   const result= await creditControlService.addCreditById(req);
   if(result){
    res.message = _localize('module.update', req, 'credit');
    return util.successResponse(result, res);
   }
   return util.failureResponse(_localize('module.updateError', req, 'credit'), res);
})

module.exports = {
    addCreditById,
}