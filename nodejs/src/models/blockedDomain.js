const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;

const schema = new Schema(
    {
        domain: {
            type: String,
            required: true,
            unique: true,
            lowercase: true,
            trim: true
        },
        reason: {
            type: String,
            default: ''
        },
        isActive: {
            type: Boolean,
            default: true
        },
        createdBy: {
            type: Schema.Types.ObjectId,
            ref: 'user'
        },
        updatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user'
        },
        deletedAt: { type: Date }
    },
    { timestamps: true }
);

schema.plugin(mongoosePaginate);

const blockedDomain = mongoose.model('blockedDomain', schema, 'blockedDomains');

module.exports = blockedDomain; 