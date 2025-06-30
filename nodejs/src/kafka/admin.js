const { kafka } = require('./client');

/**
 * Creates a Kafka topic with the specified name and number of partitions.
 * @param {string} topicnm - The name of the Kafka topic to be created.
 * @param {number} partition - The number of partitions for the created topic.
 * @returns {Promise<void>} - A promise representing the asynchronous execution of the topic creation process.
 */

async function createTopic(topicnm, partition) {
    try {
        // Create a Kafka admin instance.
        const admin = kafka.admin();

        // Connect to the Kafka broker.
        await admin.connect();
        logger.info('Admin connected successfully');

        const existingTopics = await admin.listTopics();
        if (existingTopics.includes(topicnm)) {
            logger.info(`${topicnm} topic already exists, skipping creation`);
        } else {
            // Create the specified topic with the given number of partitions.
            await admin.createTopics({
                topics: [
                    {
                        topic: topicnm,
                        numPartitions: partition,
                    },
                ],
            });
            logger.info(`${topicnm} topic created successfully with ${partition} partition`);
        }

        // Disconnect the admin after creating the topic.
        await admin.disconnect();
        logger.info('Admin is disconnected');
    } catch (error) {
        logger.error('Error - createTopic', error);
    }
}

module.exports = {
    createTopic,
};
