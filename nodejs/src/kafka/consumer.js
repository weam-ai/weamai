const { kafka } = require('./client');

/**
 * Consumes messages from a Kafka topic within a specified consumer group.
 * @param {string} group - The consumer group to which the consumer belongs.
 * @param {string} topicnm - The name of the Kafka topic from which messages will be consumed.
 * @returns {Promise<void>} - A promise representing the asynchronous execution of the message consumption process.
 */

async function consumeKafkaMessages(group, topicnm) {
    // Create a Kafka consumer instance with the specified consumer group.
    const consumer = kafka.consumer({ groupId: group });

    try {
        // Connect to the Kafka broker.
        await consumer.connect();
        logger.info('Consumer connected successfully');

        // Subscribe to the specified Kafka topic, starting from the beginning.
        await consumer.subscribe({
            topics: [topicnm],
            fromBeginning: true,
        });
        logger.info(`Consumer subscribed to the ${topicnm} topic`);

        // Run the consumer, handling each received message asynchronously.
        await consumer.run({
            eachMessage: async ({ topic, partition, message }) => {
                logger.info(
                    `${group}: [${topic}]: PART:${partition}: ${message.value.toString()}`,
                );
            },
        });

        logger.info('All messages are consumed');
    } catch (error) {
        logger.error('Error - consumeKafkaMessages', error);
    }
}

module.exports = {
    consumeKafkaMessages
}
