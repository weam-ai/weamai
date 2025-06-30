const notificationService = require('../../services/notification');

const saveToken = catchAsync(async (req, res) => {
    await notificationService.createOrUpdateToken(req);
    res.message = _localize('module.tokenUpdated', req);
    return util.successResponse(null, res);
});

const getAll = catchAsync(async (req, res) => {
    const result = await notificationService.getAll(req);
    if (result.data.length) {
        res.message = _localize('module.list', req, 'notification');
        return util.successListResponse(result, res);
    }
    res.message = _localize('module.notFound', req, 'notification');
    return util.recordNotFound(null, res);
});

const sendManualPushNotification = catchAsync(async (req, res) => {
    const body = req.body;
    const notification = {
        title: 'Test Notification',
        body: 'Hello!!😃 this is the test notification Of custom ai 😃',
    };
    await notificationService.sendPushNotificationToUsers({
        fcmTokens: [body.token],
        notificationPayload: notification,
    });
    return util.successResponse(null, res);
});

const updateReadStatus = catchAsync(async (req, res) => {
    const result = await notificationService.updateReadStatus(req);
    res.message = _localize('module.update', req, 'notification');
    return util.successResponse(result, res);
})

const notificationCount = catchAsync(async (req, res) => {
    const result = await notificationService.notificationCount(req);
    res.message = _localize('module.get', req, 'notification Count');
    return util.successResponse(result, res);
})

const deleteAll = catchAsync(async (req, res) => {
    const result = await notificationService.deleteAll(req);
    res.message = _localize('module.delete', req, 'notification');
    return util.successResponse(result, res);
})

module.exports = {
    saveToken,
    getAll,
    sendManualPushNotification,
    updateReadStatus,
    notificationCount,
    deleteAll
};
