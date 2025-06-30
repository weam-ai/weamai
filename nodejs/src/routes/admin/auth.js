const express = require('express');
const authController = require('../../controller/admin/authController');
const {
    signInSchemaKeys,
    commonSignupKeys,
    resendOtpKeys,
    changePasswordKeys,
    forgotPasswordKeys,
    resetPasswordKeys,
    verifyOtpKeys,
    mfaLogin,
    mfaStatusKeys
} = require('../../utils/validations/auth');
const {
    authentication,
    checkPermission,
} = require('../../middleware/authentication');
const { checkPromptLimit } = require('../../middleware/promptlimit');

const router = express.Router();

router
    .post(
        '/invite',
        validate(commonSignupKeys),
        authentication,
        checkPermission,
        checkPromptLimit,
        authController.inviteUsers,
    )
    .descriptor('auth.invite');
router.post('/signin', validate(signInSchemaKeys), authController.logIn);
router.post('/refresh-token', authController.refreshToken);
router.post(
    '/resend-otp',
    validate(resendOtpKeys),
    authController.resendLoginOtp,
);
router
    .post(
        '/change-password',
        validate(changePasswordKeys),
        authentication,
        checkPermission,
        authController.changePassword,
    )
    .descriptor('auth.passwordchange');
router.post(
    '/forgot-password',
    validate(forgotPasswordKeys),
    authController.forgotPassword,
);
router.post(
    '/reset-password',
    validate(resetPasswordKeys),
    authController.resetPassword,
);
router
    .get(
        '/profile/:id',
        authentication,
        checkPermission,
        authController.viewProfile,
    )
    .descriptor('auth.viewprofile');
router
    .put(
        '/update-profile/:id',
        authentication,
        checkPermission,
        authController.updateProfile,
    )
    .descriptor('auth.updateprofile');
router.post('/verify-otp', validate(verifyOtpKeys), authController.verifyLoginOtp);
router.post('/logout', authController.logout)
router.post('/mfa-login', validate(mfaLogin), authController.mfaLogin);
router.post('/generate-mfa-secret', validate(mfaStatusKeys), authentication, authController.generateMfaSecret);
router.post('/verify-mfa-otp', validate(verifyOtpKeys), authController.verifyMfaOtp);

module.exports = router;
