const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { userSchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;

const schema = new Schema(
    {
        user: userSchema,
        notificationId: {
            type: Schema.Types.ObjectId,
            ref: 'notification'
        },
        workspaceId: {
            type: Schema.Types.ObjectId,
            ref: 'workspace'
        },
        chatId: {
            type: Schema.Types.ObjectId,
            ref: 'chat'
        },
        brainId: {
            type: Schema.Types.ObjectId,
            ref: 'brain'
        },
        messageId: {
            type: Schema.Types.ObjectId,
            ref: 'messages'
        },
        threadId: {
            type: Schema.Types.ObjectId,
            ref: 'replythread'
        },
        threadType: { type: String }, // for notification click 
        msg: {
            type: String,
        },
        isRead: {
            type: Boolean,
            default: false
        },
        type: {
            type: Number, // 1 for push notification
        },
        updatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        deletedAt: { type: Date },
        sender: userSchema
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const notificationList = mongoose.model('notificationList', schema, 'notificationList');

module.exports = notificationList;
