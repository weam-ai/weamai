const express = require('express');
const router = express.Router();
const authController = require('../../controller/web/authController');
const { authentication } = require('../../middleware/authentication');
const {
    changePasswordKeys,
    forgotPasswordKeys,
    signInSchemaKeys,
    verifyOtpKeys,
    resendOtpKeys,
    resetPasswordKeys,
    inviteLoginKeys,
    mfaStatusKeys,
    mfaLogin,
    onBoardProfileKeys
} = require('../../utils/validations/auth');
const { updateSchemaKeys } = require('../../utils/validations/user');
const { normalMedia } = require('../../middleware/multer');
const { apiBasicAuth } = require('../../middleware/apiBasicAuth');

router.post('/signin', validate(signInSchemaKeys), authController.logIn);
router.post('/mfa-login', validate(mfaLogin), authController.mfaLogin);
router.post('/generate-mfa-secret', validate(mfaStatusKeys), authentication, authController.generateMfaSecret);
router.post('/verify-otp', validate(verifyOtpKeys), authentication, authController.verifyLoginOtp);
router.post('/resend-otp', validate(resendOtpKeys), authController.resendLoginOtp);
router.post('/change-password', validate(changePasswordKeys), authentication, authController.changePassword);
router.post('/forgot-password', validate(forgotPasswordKeys), authController.forgotPassword);
router.post('/reset-password', validate(resetPasswordKeys), authController.resetPassword);
router.get('/profile/:id', authentication, authController.viewProfile);
router.put('/update-profile/:id', normalMedia.single('coverImg'), validate(updateSchemaKeys), authentication, authController.updateProfile);
router.post('/invite-login', validate(inviteLoginKeys), authController.inviteLogin);
router.post('/logout', authController.logout);
router.post('/refresh-token', authController.refreshToken);
router.post('/verify-mfa-otp', validate(verifyOtpKeys), authController.verifyMfaOtp);
router.post('/onboard-profile', validate(onBoardProfileKeys), authentication, authController.onBoardProfile);
router.post('/seed-general-brain', apiBasicAuth, authController.seedGeneralBrain);
module.exports = router;