const jwt = require('jsonwebtoken');
const { JWT_STRING } = require('../config/constants/common');
const { AUTH } = require('../config/config');
const User = require('../models/user');
const Role = require('../models/role');
const Company = require('../models/company');
const { permit } = require('../services/rolePermission');

const authentication = catchAsync(async (req, res, next) => {
    try {
        const token = req.headers['authorization']?.split(JWT_STRING)[1] || req.query.authorization?.split(JWT_STRING)[1];

        if (!token) {
            res.message = _localize('auth.unAuthenticated', req);
            return util.tokenNotProvided(res);
        }

        const decode = jwt.verify(token, AUTH.JWT_SECRET);

        const existingUser = await User.findOne({ email: decode.email });

        if (!existingUser) {
            res.message = _localize('auth.account_not_found', req, 'email');
            return util.userNotFound(res);
        }

        const [companyData, existingRole] = await Promise.all([
            Company.findById({ _id: existingUser.company.id },{countryName:1}),
            Role.findById({ _id: existingUser.roleId, isActive: true })
        ]);

        if (!existingRole) {
            res.message = _localize('auth.unAuthenticated', req);
            return util.unAuthenticated(res);
        }
        req.user = existingUser
        req.userId = existingUser._id;
        req.roleId = existingRole._id;
        req.roleCode = existingRole.code;
        req.countryName = companyData?.countryName;

        next();
    } catch (error) {
        return util.unAuthenticated(res);
    }
})

const checkPermission = catchAsync(async(req, res, next) => {
    try {
        const result = await permit(req);
        if (result) {
            const user = req.user;
            if (req.method !== 'GET') {
                if (req.method === 'POST') {
                    req.body.createdBy = user._id;
                } else if (req.method === 'PUT') {
                    const softDelete = req.originalUrl.search('soft-delete');
                    if (softDelete !== -1) {
                        req.body.deletedBy = user._id;
                    }
                }
                req.body.updatedBy = user._id;
            }

            next();
        } else {
            res.message = _localize('auth.permission', req);
            return util.unAuthorizedRequest(res);
        }
    } catch (error) {
        return util.unAuthorizedRequest(res);
    }
})

const checkRole = catchAsync(async (req, res, next) => {
    try {
        if (req.roleCode != ROLE_TYPE.COMPANY) {
            res.message = _localize('auth.invalid_role', req);
            return util.unAuthorizedRequest(res);
        }
        next();
    } catch (error) {
        return util.unAuthorizedRequest(res);
    }
});

module.exports = {
    authentication,
    checkPermission,
    checkRole,
}