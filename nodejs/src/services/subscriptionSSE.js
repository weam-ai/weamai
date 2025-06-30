const crypto = require('crypto');
const logger = require('../utils/logger');
const { sseEmitter, ssePubClient } = require('../sse/sseRedis');
const { LINK } = require('../config/config');
const { subscriptionQueue } = require('../jobs/configuration');
const { createJob } = require('../jobs');
const { JOB_TYPE } = require('../config/constants/common');
const { checkSubscription } = require('./auth');

const connectedClients= {}

const subscriptionSSEEvent = async (req, res) => {
    try {
        if (res.headersSent) {
            throw new Error('Headers already sent');
        }

        const companyId = req.user.company.id;
        if (!companyId) {
            throw new Error('Company ID not found');
        }

        // Set SSE headers
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': LINK.FRONT_URL, 
            'Access-Control-Allow-Credentials': true
        }); 

        const userId = req.user.id;
        // Generate a more unique connection ID using UUID or similar
        const connectionId = `${Date.now()}-${crypto.randomUUID()}-${userId}`;

        // Initialize client tracking structures
        if (!connectedClients[companyId]) {
            connectedClients[companyId] = {};
        }
        if (!connectedClients[companyId][userId]) {
            connectedClients[companyId][userId] = [];
        }

        // Add the response object to the user's connections
        connectedClients[companyId][userId].push({ res, connectionId });

        const subscription = await checkSubscription(req);


        // await createJob(JOB_TYPE.SEND_SUBSCRIPTION, {
        //     data: { companyId,status:subscription?.status }
        // });
        // Handle client disconnect
        req.on('close', async () => {

            // Remove the specific connection
            connectedClients[companyId][userId] = connectedClients[companyId][userId]
                .filter(conn => conn.connectionId !== connectionId);
            
            if (connectedClients[companyId][userId].length === 0) {
                delete connectedClients[companyId][userId];
            }
            if (connectedClients[companyId] && Object.keys(connectedClients[companyId]).length === 0) {
                delete connectedClients[companyId];
            }


            logger.info(`SSE connection closed: ${connectionId}`);
        });
    } catch (error) {
        logger.error('SSE subscriptionSSEEvent Error:', error);
        if (!res.headersSent) {
            res.status(500).json({ 
                error: 'Failed to establish SSE connection',
                message: error.message 
            });
        }
    }
};


// Listen for SSE events from Redis Pub/Sub and broadcast to connected clients
// sseEmitter.on('broadcast', async (eventData) => {
//     try {
//         await createJob(JOB_TYPE.SEND_SUBSCRIPTION, eventData);
        
//         logger.verbose(`Job added to queue for subscription`);
//     } catch (error) {
//         logger.error('Failed to add job to queue:', error);
//     }
// });

// // Add these listeners after importing subscriptionQueue
// subscriptionQueue.on('waiting', (jobId) => {
//     logger.info(`Job ${jobId} is waiting`);
// });

// subscriptionQueue.on('active', (job) => {
//     logger.info(`Job ${job.id} has started processing`);
// });

// subscriptionQueue.on('completed', (job) => {
//     logger.info(`Job ${job.id} has completed`);
// });

// subscriptionQueue.on('failed', (job, error) => {
//     logger.error(`Job ${job.id} has failed:`, error);
// });

// // You can also check queue status
// const checkQueueStatus = async () => {
//     const jobCounts = await subscriptionQueue.getJobCounts();
//     logger.info('Queue status:', jobCounts);
//     // Will show waiting, active, completed, failed, delayed, paused
// };

// // Check status every minute
// setInterval(checkQueueStatus, 60000);

module.exports = {
    subscriptionSSEEvent,
    connectedClients
}


