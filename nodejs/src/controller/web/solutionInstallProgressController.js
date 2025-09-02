const solutionInstallService = require('../../services/solutionInstall');
const { catchAsync } = require('../../utils/helper');
const util = require('../../utils/util');
const { _localize } = require('../../utils/localization');
const jwt = require('jsonwebtoken');
const { JWT_STRING } = require('../../config/constants/common');
const { AUTH } = require('../../config/config');
const User = require('../../models/user');
const Role = require('../../models/role');
const Company = require('../../models/company');

const getInstallationProgress = catchAsync(async (req, res) => {
    // Handle token authentication from query parameter
    const token = req.query.token;
    if (!token) {
        return res.status(401).json({ message: 'Token required' });
    }

    // Verify the token and get user data
    try {
        const decode = jwt.verify(token, AUTH.JWT_SECRET);
        const existingUser = await User.findOne({ email: decode.email });

        if (!existingUser) {
            return res.status(401).json({ message: 'User not found' });
        }

        const [companyData, existingRole] = await Promise.all([
            Company.findById({ _id: existingUser.company.id }, { countryName: 1 }),
            Role.findById({ _id: existingUser.roleId, isActive: true })
        ]);

        if (!existingRole) {
            return res.status(401).json({ message: 'Invalid role' });
        }

        req.user = existingUser;
        req.userId = existingUser._id;
        req.roleId = existingRole._id;
        req.roleCode = existingRole.code;
        req.countryName = companyData?.countryName;
    } catch (error) {
        return res.status(401).json({ message: 'Invalid token' });
    }

    // Set SSE headers
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
    });

    // Send initial connection message
    res.write(`data: ${JSON.stringify({ 
        type: 'connected', 
        message: 'Connected to installation progress stream' 
    })}\n\n`);

    // Start the installation process
    try {
        await solutionInstallService.installWithProgress(req, res);
    } catch (error) {
        res.write(`data: ${JSON.stringify({ 
            type: 'error', 
            message: error.message || 'Installation failed' 
        })}\n\n`);
    }

    // Close the connection
    res.end();
});

module.exports = {
    getInstallationProgress
};
