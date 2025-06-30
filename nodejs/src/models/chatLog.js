const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;

const schema = new Schema(
    {
        botId: {
            type: Schema.Types.ObjectId,
            ref: 'bot',
        },
        userId: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        msg: {
            type: String
        },
        isActive: {
            type: Boolean,
            default: true,
        },
        createdBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        updatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        deletedAt: { type: Date },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const chatlog = mongoose.model('chatlog', schema);

module.exports = chatlog;
