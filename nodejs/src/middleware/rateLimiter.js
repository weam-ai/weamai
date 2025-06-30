const { rateLimit } = require('express-rate-limit');
const { API_RATE_LIMIT } = require('../config/config');

const rateLimitMiddleware = rateLimit({
    windowMs: 60 * 1000,
    limit: API_RATE_LIMIT,
    standardHeaders: 'draft-7',
    legacyHeaders: false,
    message: `You have exceeded your ${API_RATE_LIMIT} requests per minute limit.`
})

module.exports = rateLimitMiddleware;