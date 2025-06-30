const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { LOG_STATUS, CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;
const schema = new Schema(
    {
        type: {
            type: String, // FORGOT_PASSWORD MAIL, LOGIN_OTP SEND
            index: true,
        },
        status: {
            type: String,
            default: LOG_STATUS.PENDING,
            index: true,
        },
        data: {
            type: JSON,
        },
        response: {
            type: JSON,
        },
        isActive: {
            type: Boolean
        },
        createdBy: { type: Object },

        updatedBy: { type: Object },
    },
    {
        timestamps: {
            createdAt: 'createdAt',
            updatedAt: 'updatedAt',
        },
    },
);

schema.pre('save', async function (next) {
    this.isActive = true;
    next();
});

schema.method('toJSON', function () {
    const { __v, _id, ...object } = this.toObject();
    object.id = _id;
    return object;
});

schema.plugin(mongoosePaginate);

const log = mongoose.model('log', schema, 'log');

module.exports = log;