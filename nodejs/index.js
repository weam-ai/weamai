const app = require('./app');
const { SERVER } = require('./src/config/config');
const http = require('http');
const server = http.createServer(app);
const socketIo = require('socket.io');
global.io = socketIo(server,{
    path: '/napi/socket.io',
    cors: {
        origin: "*",
        methods: ['GET', 'POST'],
        credentials: true
    },
    transports: [ 'websocket' ],
});

require('./src/socket/rooms');
require('./src/socket/chat');
const { pubClient, subClient } = require('./src/socket/rooms');

server.listen(SERVER.PORT, async () => {
    await Promise.all([pubClient.connect(), subClient.connect()]);
    logger.info(`Backend server is started on port ${SERVER.PORT}`);
});
