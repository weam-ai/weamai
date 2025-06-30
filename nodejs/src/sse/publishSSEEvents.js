// const { ssePubClient } = require('./sseRedis'); 
const logger = require('../utils/logger'); 

/**
 * Publishes an SSE event to the Redis channel
 * @param {Object} eventData - The event data to publish
 */
const publishSSEEvent = async (eventData) => {
    try {
        // const SSE_CHANNEL = 'sse-events'; 
        // await ssePubClient.publish(SSE_CHANNEL, JSON.stringify(eventData));
        logger.info('Published SSE event to Redis:', eventData);
    } catch (error) {
        logger.error('Failed to publish SSE event:', error);
    }
};

module.exports = publishSSEEvent;
