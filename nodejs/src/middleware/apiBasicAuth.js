const config = require('../config/config')

const getCredentials = (req) => {
    const authHeader = req.headers.authorization
    if (!authHeader) {
        res.message = _localize('auth.unAuthenticated', req)
        return util.tokenNotProvided(res)
    }
    if (!authHeader.startsWith('Basic ')) {
        res.message = _localize('auth.unAuthenticated', req)
        return util.tokenNotProvided(res)
    }
    const base64Credentials = authHeader.split(' ')[1]
    const credentials = Buffer.from(base64Credentials, 'base64').toString('utf8')
    const [username, password] = credentials.split(':')
    return { username, password }
}

const apiBasicAuth = (req, res, next) => {
    try {
        const { username, password } = getCredentials(req)
        if (username === config.API.BASIC_AUTH_USERNAME && password === config.API.BASIC_AUTH_PASSWORD) next()
        else return util.unAuthenticated(res)
    } catch (error) {
        return util.unAuthenticated(res)
    }
}

const deviceBasicAuth = (req, res, next) => {
    try {
        const { username, password } = getCredentials(req)
        if (username === config.API.BASIC_AUTH_USERNAME && password === config.API.BASIC_AUTH_PASSWORD) next()
        else return util.unAuthenticated(res)
    } catch (error) {
        return util.unAuthenticated(res)
    }
}

module.exports = {
    apiBasicAuth,
    deviceBasicAuth,
}
