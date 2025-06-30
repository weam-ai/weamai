const disposableDomains = require('disposable-email-domains');
const BlockedDomain = require('../../models/blockedDomain');

const isDisposableEmail = (email) => {
    const domain = email.split('@')[1];
    return disposableDomains.includes(domain);
};

const isBlockedDomain = async (email) => {
    const domain = email.split('@')[1];
    const blocked = await BlockedDomain.findOne({ 
        domain: domain.toLowerCase(),
        isActive: true,
        deletedAt: null 
    });
    return !!blocked;
};

const validateEmail = async (email) => {
    if (!email) return false;

    // Check if domain is blocked
    if (await isBlockedDomain(email)) {
        return false;
    }
    // Check if it's a disposable email
    if (isDisposableEmail(email)) {
        return false;
    }

    return true;
};

module.exports = {
    isDisposableEmail,
    isBlockedDomain,
    validateEmail
}; 