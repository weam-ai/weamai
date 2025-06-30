const mongoose = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const {
    CUSTOM_PAGINATE_LABELS,
    PAYMENT_TYPE,
} = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;
const schema = new Schema(
    {
        companyId: {
            type: Schema.Types.ObjectId,
            ref: 'company',
        },
        sts: {
            type: Number,
            default: PAYMENT_TYPE.PENDING,
        },
        amount: {
            type: Number,
        },
        isActive: {
            type: Boolean,
            default: true,
        },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const payment = mongoose.model('payment', schema, 'payment');

module.exports = payment;