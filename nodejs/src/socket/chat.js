const { SOCKET_EVENTS } = require("../config/constants/socket");
const { SOCKET_ROOM_PREFIX } = require("../config/constants/socket");

const sendThread = (chatId, data) => {
    let sockets = global.io.sockets;
    sockets.to(`${SOCKET_ROOM_PREFIX.CHAT}${chatId}`).emit(SOCKET_EVENTS.THREAD, data);
}

const sendUserQuery = (chatId, data) => {
    const sockets = global.io.sockets;
    const room = `${SOCKET_ROOM_PREFIX.CHAT}${chatId}`;
    sockets.to(room).emit(SOCKET_EVENTS.USER_QUERY, data);
}

const sendAiModelKeyRemove = (companyId, data) => {
    const sockets = global.io.sockets; 
    const room = `${SOCKET_ROOM_PREFIX.COMPANY}${companyId}`;
    sockets.to(room).emit(SOCKET_EVENTS.AI_MODEL_KEY_REMOVE, data);
}

const sendUserSubscriptionUpdate = (companyId, data) => {
    const sockets = global.io.sockets; 
    const room = `${SOCKET_ROOM_PREFIX.COMPANY}${companyId}`;
    sockets.to(room).emit(SOCKET_EVENTS.USER_SUBSCRIPTION_UPDATE, data);
}

module.exports = {
    sendThread,
    sendUserQuery,
    sendAiModelKeyRemove,
    sendUserSubscriptionUpdate
}