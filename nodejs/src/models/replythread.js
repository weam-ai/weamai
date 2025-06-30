const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { userSchema, fileSchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        chatId: {
            type: Schema.Types.ObjectId,
            ref: 'chat',
        },
        messageId: {
            type: Schema.Types.ObjectId,
            ref: 'messages',
        },
        sender: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        type: { type: String }, // for separate question and answer thread
        content: { type: String },
        attachment: [fileSchema],
        reaction: [
            {
                user: {
                    type: Schema.Types.ObjectId,
                    ref: 'user',
                },
                emoji: {
                    type: Schema.Types.Mixed,
                }
            }
        ],
        tagusers: [
            {
                type: Schema.Types.ObjectId,
                ref: 'user',
            }
        ],
        isActive: {
            type: Boolean,
            default: true,
        },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const replythread = model('replythread', schema, 'replythread');

module.exports = replythread;
