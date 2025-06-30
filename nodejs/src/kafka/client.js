const { Kafka } = require('kafkajs');
const { KAFKA } = require('../config/config');

const kafka = new Kafka({
    clientId: KAFKA.CLIENT_ID,
    brokers: [`${KAFKA.PRIVATE_HOST}:${KAFKA.PRIVATE_PORT}`]
})

module.exports = {
    kafka
}