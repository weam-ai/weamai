const { kafka } = require('./client');

/**
 * Produces Kafka messages to a specified topic with optional partition, message key, and message payload.
 * @param {string} topicnm - The name of the Kafka topic to which messages will be produced.
 * @param {number} partition - The partition number for the message (optional).
 * @param {string} msgKey - The key associated with the message (optional).
 * @param {Object} message - The payload of the Kafka message, typically an object to be stringified (optional).
 * @returns {Promise<void>} - A promise representing the asynchronous execution of the message production process.
 */

async function produceKafkaMessages(topicnm, message) {
    let producer;

    try {
        // Create a Kafka producer instance.
        producer = kafka.producer();

        // Connect to the Kafka broker.
        await producer.connect();
        logger.info('Producer Connected Successfully');

        logger.info('Sending kafka message process start');

        // Send the message to the specified Kafka topic with optional partition, message key, and payload.
        await producer.send({
            topic: topicnm,
            messages: [
                {
                    value: JSON.stringify(message),
                },
            ],
        });

        logger.info('Sending kafka message process finish');
    } catch (error) {
        logger.error('Error - produceKafkaMessages', error);
    } finally {
        try {
            // Disconnect the producer after sending the message (whether successful or not).
            if (producer) {
                await producer.disconnect();
                logger.info('Producer Disconnected Successfully');
            }
        } catch (disconnectError) {
            logger.error('Error disconnecting producer', disconnectError);
        }
    }
}

module.exports = {
    produceKafkaMessages,
};
