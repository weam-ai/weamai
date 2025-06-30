const { _processors } = require('./jobservice');
const { defaultQueue, mailQueue, notificationQueue, subscriptionQueue } = require('./configuration');

for (let identity in _processors) {
    defaultQueue.process(identity, 3, _processors[identity]);
    mailQueue.process(identity, 5, _processors[identity]);
    notificationQueue.process(identity, 5, _processors[identity]);
    subscriptionQueue.process(identity, 5, _processors[identity]);
}