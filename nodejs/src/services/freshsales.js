const config = require('../config/config');
const Company = require('../models/company');

const createFreshCRMContact = async (contact) => {
    const url = `https://${config.FRESHSALES.DOMAIN}/api/contacts`
    const apiKey = config.FRESHSALES.API_KEY

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                Authorization: `Token token=${apiKey}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contact: {
                    first_name: contact.firstName,
                    last_name: contact.lastName,
                    email: contact.email,
                    custom_field: {
                        cf_is_active: true,
                        cf_company: contact.companyName,
                    },
                },
            }),
        })

        const data = await response.json()
        if (!response.ok) {
            logger.error('Error - createFreshCRMContact', data);
            return null
        }
        await Company.updateOne({ _id: contact.companyId }, { $set: { freshCRMContactId: data.contact.id } });
        return data
    } catch (error) {
        logger.error('Error - createFreshCRMContact', error)
    }
}

const updateCRMSubscriptionStatus = async (contactId, plan, status, reason) => {
    const response = await fetch(`https://${config.FRESHSALES.DOMAIN}/api/contacts/${contactId}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Token token=${config.FRESHSALES.API_KEY}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            contact: {
                custom_field: {
                    cf_subscription_plan: plan,
                    cf_plan_status: status,
                    ...(reason && { cf_cancellation_reason: reason })
                }
            }
        })
    });

    const data = await response.json();
    if (!response.ok) {
        logger.error('Error updating subscription:', data);
        return null;
    } 
    return data;
};
  

module.exports = {
    createFreshCRMContact,
    updateCRMSubscriptionStatus,
}
