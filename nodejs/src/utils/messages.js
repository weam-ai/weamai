const responseStatusCode = require('./responseCode');
const { RESPONSE_CODE } = require('../config/constants/common');
const { INVITE_SUBSCRIPTION_ERROR } = require('../config/constants/aimodal');

exports.unAuthenticated = (res) => {
    return res.status(responseStatusCode.unAuthenticated).json({
        status: responseStatusCode.unAuthenticated,
        code: RESPONSE_CODE.UNAUTHENTICATED,
        message: res.message,
        data: {},
    });
};

exports.successResponse = (data, res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.DEFAULT,
        message: res.message,
        data: data,
    });
};

exports.failedSoftDelete = (res) => {
    res.MESSAGE = 'Data can not be soft delete due to internal server error';
    return res.status(responseStatusCode.internalServerError).json({
        status: responseStatusCode.internalServerError,
        STATUS: 'FAILURE',
        MESSAGE: 'Data can not be soft delete due to internal server error',
        DATA: {},
    });
};

exports.createdDocumentResponse = (data, res) => {
    return res.status(responseStatusCode.create).json({
        status: responseStatusCode.create,
        code: RESPONSE_CODE.DEFAULT,
        message: res.message,
        data: data,
    });
};

exports.emailSendSuccessfully = (res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.DEFAULT,
        message: res.message,
        data: {},
    });
};

exports.sendEmailFailed = (res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: {},
    });
};

exports.emailVerifySuccess = (res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        CODE: RESPONSE_CODE.DEFAULT,
        MESSAGE: res.message,
        data: {},
    });
};

exports.linkInvalid = (res) => {
    return res.status(responseStatusCode.validationError).json({
        status: responseStatusCode.validationError,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: {},
    });
};

exports.changePasswordResponse = (res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.DEFAULT,
        message: res.message,
        data: {},
    });
};

exports.wrongPassword = (res) => {
    return res.status(responseStatusCode.validationError).json({
        status: responseStatusCode.validationError,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: {},
    });
};

exports.updateProfileResponse = (data, res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.DEFAULT,
        message: res.message,
        data: data,
    });
};

exports.failureResponse = (data, res) => {
    let i = 0;
    if (data && data.name === 'ValidationError') {
        Object.keys(data.errors).forEach((key) => {
            if (i !== 1) {
                data.message = data.errors[key].message;
            }
            i++;
        });
    }
    res.message =
        data && data.message ? data.message : res.message ? res.message : data;
    return res.status(responseStatusCode.validationError).json({
        status: responseStatusCode.validationError,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
    });
};

exports.badRequest = (data, res) => {
    return res.status(responseStatusCode.badRequest).json({
        status: responseStatusCode.badRequest,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: data,
    });
};

exports.recordNotFound = (data, res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.NOT_FOUND,
        message: res.message,
        data: [],
    });
};

exports.insufficientParameters = (res) => {
    return res.status(responseStatusCode.badRequest).json({
        status: responseStatusCode.badRequest,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: {},
    });
};

exports.notFound = (err, res) => {
    return res.status(responseStatusCode.validationError).json({
        status: responseStatusCode.validationError,
        code: RESPONSE_CODE.NOT_FOUND,
        message: err,
        data: {},
    });
};

exports.inValidParam = (message, res) => {
    message = message ? message.replace(/"/g, '') : message;
    res.message = message;
    return res.status(responseStatusCode.validationError).json({
        status: responseStatusCode.validationError,
        code: RESPONSE_CODE.ERROR,
        message: message,
        data: {},
    });
};

exports.unAuthorizedRequest = (res) => {
    return res.status(responseStatusCode.unAuthorizedRequest).json({
        status: responseStatusCode.unAuthorizedRequest,
        code: RESPONSE_CODE.UNAUTHENTICATED,
        message: res.message,
        data: {},
    });
};

exports.loginSuccess = async (result, res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.LOGIN,
        message: res.message,
        data: result,
    });
};

exports.verificationOTP = (result, res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.OTP,
        message: res.message,
        data: result.token ? result : { message: result },
    });
};

exports.passwordEmailWrong = (res) => {
    return res.status(responseStatusCode.unAuthorizedRequest).json({
        status: responseStatusCode.unAuthorizedRequest,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: {},
    });
};

exports.passwordNotSet = (res) => {
    return res.status(responseStatusCode.unAuthorizedRequest).json({
        status: responseStatusCode.unAuthorizedRequest,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: {},
    });
};

exports.loginFailed = (res, statusCode) => {
    return res
        .status(
            statusCode === 410
                ? responseStatusCode.linkExpire
                : responseStatusCode.unAuthenticated
        )
        .json({
            status:
                statusCode === 410
                    ? responseStatusCode.linkExpire
                    : responseStatusCode.unAuthenticated,
            code: RESPONSE_CODE.ERROR,
            message:
                statusCode === 410 ? INVITE_SUBSCRIPTION_ERROR : res.message,
            data:  {},
        });
};

exports.userNotFound = (res) => {
    return res.status(responseStatusCode.unAuthenticated).json({
        status: responseStatusCode.unAuthenticated,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: {},
    });
};

exports.logoutSuccessfull = (result, res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.DEFAULT,
        message: res.message,
        data: result,
    });
};

exports.changePasswordFailResponse = (res) => {
    return res.status(responseStatusCode.validationError).json({
        status: responseStatusCode.validationError,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
    });
};

exports.loginOtpVerified = (data, res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.OTP,
        message: res.message,
        data: data,
    });
};

exports.loginOtpVerificationFailed = (data, res) => {
    return res.status(responseStatusCode.validationError).json({
        status: responseStatusCode.validationError,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: data,
    });
};

exports.successListResponse = (result, res) => {
    return res.status(responseStatusCode.success).json({
        status: responseStatusCode.success,
        code: RESPONSE_CODE.DEFAULT,
        message: res.message,
        data: result.data,
        paginator: result.paginator,
    });
};

exports.loginApiUserFailed = (res) => {
    return res.status(responseStatusCode.badRequest).json({
        status: responseStatusCode.badRequest,
        code: RESPONSE_CODE.ERROR,
        message: res.message,
        data: {},
    });
};

exports.tokenNotProvided = (res) => {
    return res.status(responseStatusCode.unAuthenticated).json({
        status: responseStatusCode.unAuthenticated,
        code: RESPONSE_CODE.TOKEN_NOT_FOUND,
        message: res.message,
        data: {},
    });
};

exports.redirectResponse = (res) =>{
    return res.status(responseStatusCode.redirect).json({
        status: responseStatusCode.redirect,
        code: RESPONSE_CODE.REDIRECT,
        message: res.message,
        data: {},
    });
}

exports.linkExpired = (res)=>{
    return res.status(responseStatusCode.linkExpire).json({
        status: responseStatusCode.linkExpire,
        code: RESPONSE_CODE.LINK_EXPIRED,
        message: res.message,
        data: {},
    })
}

exports.resendEmailLink = (res, data) => {
    return res.status(responseStatusCode.linkExpire).json({
        status: responseStatusCode.linkExpire,
        code: RESPONSE_CODE.RESEND_LINK,
        message: res.message,
        data: data,
    })
}