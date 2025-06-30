const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };
const Schema = mongoose.Schema;

const schema = new Schema(
    {
        title: {
            type: String,
        },
        body: {
            type: String,
        },
        code: {
            type: String,
        },
        createdBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        updatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        deletedAt: {
            type: Date,
        },
        deletedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        isActive: { type: Boolean, default: true },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const notification = mongoose.model('notification', schema, 'notification');

module.exports = notification;
