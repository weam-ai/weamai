// const { createClient } = require('redis');
// const { REDIS } = require("../config/config");

// const EventEmitter = require('events');

// class SSEEmitter extends EventEmitter {}
// const sseEmitter = new SSEEmitter();

// // Initialize Redis client for SSE publisher
// const ssePubClient = createClient({
//     url: `redis://${REDIS.HOST}:${REDIS.PORT}`,
//     // Optional: Use a different Redis database
//     // db: 1,
// });
// ssePubClient.on('error', (err) => logger.error('SSE PubClient Error:', err));

// const sseSubClient = ssePubClient.duplicate();
// sseSubClient.on('error', (err) => logger.error('SSE SubClient Error:', err));

// (async () => {
//     try {
//         await ssePubClient.connect();
//         await sseSubClient.connect();
//         logger.info('SSE Redis clients connected');

//         const SSE_CHANNEL = 'sse-events'; 
//         await sseSubClient.subscribe(SSE_CHANNEL, (message) => {
//             try {
//                 const eventData = JSON.parse(message);
//                 sseEmitter.emit('broadcast', eventData);
//             } catch (error) {
//                 logger.error('Failed to parse SSE event data:', error);
//             }
//         });

//         logger.info(`Subscribed to Redis channel: ${SSE_CHANNEL}`);
//     } catch (error) {
//         logger.error('SSE Redis connection error:', error);
//     }
// })();

// module.exports = {
//     sseEmitter,
//     ssePubClient,
//     sseSubClient,
// };
