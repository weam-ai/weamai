const { RESPONSE_CODE } = require('../../config/constants/common');
const authService = require('../../services/auth');

const resendLoginOtp = catchAsync(async (req, res) => {
    const result = await authService.resendLoginOtp(req);
    if (result) {
        res.message = _localize('auth.resend_otp', req);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('auth.otp_failed', req), res);
})

const logIn = catchAsync(async (req, res) => {
    const result = await authService.logIn(req);
    if (result) {
        res.message = _localize('auth.login_success', req);
        return util.loginSuccess(result, res);
    }
    res.message = _localize('auth.loginFailed', req);
    return util.loginFailed(res);
})

const mfaLogin = catchAsync(async (req, res) => {
    const result = await authService.mfaLogin(req);
    if (result) {
        res.message = _localize('auth.login_success', req);
        return util.loginSuccess(result, res);
    }
    res.message = _localize('auth.loginFailed', req);
    return util.loginFailed(res);
})

const refreshToken = catchAsync(async (req, res) => {
    return authService.refreshToken(req, res);
    if (result) {
        res.message = _localize('module.create', req, 'access_token');
        return util.successResponse(result, res);
    }
})

const verifyPassword = catchAsync(async (req, res) => {
    const result = await authService.verifyPassword(req);
    if (result) {
        res.message = _localize('auth.valid_link', req);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('auth.invalid_link', req));
})

const forgotPassword = catchAsync(async (req, res) => {
    const result = await authService.forgotPassword(req);
    if (result) {
        res.message = _localize('auth.email_sent', req);
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('auth.account_not_found', req, 'email'), res);
})

const resetPassword = catchAsync(async (req, res) => {
    const result = await authService.resetPassword(req);
    if (result) {
        res.message = _localize('auth.change_password', req);
        return util.changePasswordResponse(res);
    }
    res.message = result.data;
    return util.changePasswordFailResponse(res);
})

const verifyLoginOtp = catchAsync(async (req, res) => {
    const result = await authService.verifyLoginOtp(req);
    if (result) {
        res.message = _localize('auth.login_otp_verify_success', req);
        return util.loginOtpVerified(result, res);
    }
    res.message = result.data;
    return util.loginOtpVerificationFailed(result.data, res);
})

const changePassword = catchAsync(async (req, res) => {
    const result = await authService.changePassword(req);
    if (result) {
        res.message = _localize('module.update', req, 'password');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'password'), res);
})

const viewProfile = catchAsync(async (req, res) => {
    const result = await authService.viewProfile(req);
    if (result) {
        res.message = _localize('module.get', req, 'profile');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.getError', req, 'profile'), res);
})

const updateProfile = catchAsync(async (req, res) => {
    const result = await authService.updateProfile(req);
    if (result) {
        res.message = _localize('module.update', req, 'profile')
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'profile'), res);
})

const inviteLogin = catchAsync(async (req, res) => {
    const result = await authService.inviteLogin(req, res);
    if (result?.status === 410 && result?.code === RESPONSE_CODE.RESEND_LINK) {
        return util.resendEmailLink(res, result.data);
    }
    if (result?.statusCode === 410) {
        res.message = _localize('auth.loginFailed', req);
        return util.loginFailed(res, result.statusCode);
    }

    if (result) {
        res.message = _localize('auth.login_success', req);
        return util.loginSuccess(result, res);
    }
    res.message = _localize('auth.loginFailed', req);
    return util.loginFailed(res);
})

const logout = catchAsync(async (req, res) => {
    const result = await authService.logout(req);
    if (result) {
        res.message = _localize('auth.logout', req);
        return util.logoutSuccessfull(result, res);
    }
    res.message = _localize('auth.something_went_wrong', req);
    return util.badRequest(null, res);
})

const generateMfaSecret = catchAsync (async (req, res) => {
    const result = await authService.generateMfaSecret(req);
    if (result) {
        res.message = _localize('module.create', req, 'Mfa secret');
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.createError', req, 'Mfa secret'), res);
})

const verifyMfaOtp = catchAsync(async (req, res) => {
    const result = await authService.verifyMfaOtp(req);
    if (result) {
        res.message = _localize('auth.login_otp_verify_success', req);
        return util.loginOtpVerified(result, res);
    }
    res.message = result.data;
    return util.loginOtpVerificationFailed(result.data, res);
})

const onBoardProfile = catchAsync(async (req, res) => {
    const result = await authService.onBoardProfile(req);
    if (result) {
        res.message = _localize('auth.login_success', req);
        return util.loginSuccess(result, res);
    }
    res.message = _localize('auth.loginFailed', req);
    return util.loginFailed(res);
})

const seedGeneralBrain = catchAsync(async (req, res) => {
    try {
        const result = await authService.seedGeneralBrainAPI(req);
        if (result) {
            res.message = _localize('auth.create', req);
            return util.successResponse(result, res);
        }
    } catch (error) {
        return util.failureResponse(_localize('auth.create', req), res);
    }
})

const updateMcpData = catchAsync(async (req, res) => {
    const result = await authService.updateMcpData(req);
    if (result) {
        res.message = _localize('module.update', req, 'Mcp records')
        return util.successResponse(result, res);
    }
    return util.failureResponse(_localize('module.updateError', req, 'Mcp records'), res);
}) 

module.exports = {
    resendLoginOtp,
    refreshToken,
    verifyPassword,
    resetPassword,
    verifyLoginOtp,
    forgotPassword,
    changePassword,
    logIn,
    viewProfile,
    updateProfile,
    inviteLogin,
    logout,
    mfaLogin,
    generateMfaSecret,
    verifyMfaOtp,
    onBoardProfile,
    seedGeneralBrain,
    updateMcpData
}