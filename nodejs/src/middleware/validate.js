const validate = (validator) => {
    return async function (req, res, next) {
        try {
            await validator.validateAsync(req.body);
            next();
        } catch (err) {
            if (err.isJoi) return util.inValidParam(err.message, res);
            return util.failureResponse(err.message, res);
        }
    };
};

module.exports = validate;