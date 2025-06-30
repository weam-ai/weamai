const User = require('../models/user');

const setPromptLimit = async (req) => {
    try {
        const existingUser = await User.findById({ _id: req.params.id });
        if (!existingUser) return false;
        return User.findByIdAndUpdate(
            { _id: req.params.id },
            {
                promptLimit: {
                    ...req.body,
                },
            },
            {
                new: true,
            },
        );
    } catch (error) {
        handleError(error, 'Error - setPromptLimit');
    }
};

module.exports = {
    setPromptLimit,
};
