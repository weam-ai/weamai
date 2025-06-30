const { sendEmail } = require('../services/email');
const { updateDBRef, deleteDBRef } = require('../utils/helper');
const { sendPushNotification } = require('../services/notification');
const { connectedClients } = require('../services/subscriptionSSE');
const logger = require('../utils/logger');

module.exports = {
    _processors: {
        sendMail: async ({ data }) => {
            try {
                logger.info('start proccessing email sent');
                await sendEmail(data);
                logger.info('finish email sent');
                return { succeed: true };
            } catch (error) {
                logger.error('Error in email sent' + error);
                return { succeed: false };
            }
        },
        updateRef: async ({ data }) => {
            try {
                logger.info('start proccessing update db ref');
                await updateDBRef(data);
                logger.info('finish proccessing update db ref');
            } catch (error) {
                logger.error('Error in DB ref update' + error);
                return { succeed: false };
            }
        },
        deleteRef: async ({ data }) => {
            try {
                logger.info('Start proccessing to delete db ref');
                await deleteDBRef(data);
                logger.info('Finish proccessing to delete db ref');
            } catch (error) {
                logger.error('Error in DB ref delete' + error);
                return { succeed: false };
            }
        },
        sendNotification: async ({ data }) => {
            try {
                logger.info('Start proccessing to send notification');
                await sendPushNotification(data.fcmTokens, data.payload);
                logger.info('Finish proccessing to send notification');
            } catch (error) {
                logger.error('Error in send notification' + error);
                return { succeed: false };
            }
        },
        sendSubscription: async ({data}) => {

            try {
                logger.info('Processing SSE broadcast');
                const { companyId } = data.data;

                if (!connectedClients[companyId]) {
                    logger.info(`No connected clients for company ${companyId}`);
                    return { succeed: true };
                }

                Object.values(connectedClients[companyId]).forEach(userConnections => {
                    userConnections.forEach(({res}) => {
                        try {
                            res.write(`data: ${JSON.stringify(data)}\n\n`);
                        } catch (error) {
                            logger.error('Error sending SSE event to client:', error);
                            throw error; 
                        }
                    });
                });

                // return { succeed: true };
            } catch (error) {
                logger.error('Error in SSE broadcast:', error);
                return { succeed: false };
            }
        }
    }
}