const { getCompanyId, getSubscriptionStatus, isSubscriptionActive } = require("../utils/helper");
const { getUsedCredit } = require("../services/thread");
const { checkSubscription } = require("../services/auth");
const {
  EXCLUDE_COMPANY_FROM_SUBSCRIPTION,
} = require("../config/constants/common");
const Company = require("../models/company");
const moment = require("moment");

const checkPromptLimit = catchAsync(async (req, res, next) => {
  try {
    const companyId = getCompanyId(req.user);
    if (EXCLUDE_COMPANY_FROM_SUBSCRIPTION.includes(companyId.toString())) {
      return next();
    }

    const filter = {
      companyId: companyId,
    };
    const user = req.user;
    const subscriptionRecord = await getSubscriptionStatus(companyId);
    const company = await Company.findById(companyId, {
      freeTrialStartDate: 1,
    }).lean();
    const isPaid = isSubscriptionActive(subscriptionRecord?.status);
    const modelMessageCount = await getUsedCredit(
      filter,
      user,
      subscriptionRecord,
      isPaid
    );

    if (!isPaid) {
      if (
        company?.freeTrialStartDate < moment().subtract(30, "days").toDate()
      ) {
        return handleTrialExpired(req, res);
      } else if (
        modelMessageCount.msgCreditUsed > modelMessageCount.msgCreditLimit
      ) {
        return handleLimitExceeded(req, res);
      } 
      // else {
      //   return handleSubscriptionExpired(req, res);
      // }
    } else if (
      isPaid &&
      modelMessageCount.msgCreditUsed > modelMessageCount.msgCreditLimit
    ) {
      return handleSubscriptionExpired(req, res);
    }

    next();
  } catch (error) {
    logger.error("Error - checkPromptLimit", error);
  }
});

function handleLimitExceeded(req, res) {
  res.message = _localize("module.prompt_expire", req);
  return util.badRequest(null, res);
}

const handleSubscriptionExpired = (req, res) => {
  res.message = _localize("subscription.noActiveSubscription", req);
  return util.badRequest(null, res);
};

const handleTrialExpired = (req, res) => {
  res.message = _localize("module.trial_expired", req);
  return util.badRequest(null, res);
};

module.exports = {
  checkPromptLimit,
};
