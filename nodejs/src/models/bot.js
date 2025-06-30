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
        code: {
            type: String,
        },
        isActive: {
            type: Boolean,
            default: true,
        },
        seq: {
            type: Number,
        },
        createdBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        updatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        deletedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        deletedAt: { type: Date },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const bot = mongoose.model('model', schema, 'model');

module.exports = bot;
