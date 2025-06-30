const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { companySchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;

const schema = new Schema(
    {
        invoiceId: {
            type: String,
        },
        invoiceNo: {
            type: String,
        },
        interval: {
            type: String,
        },
        email: {
            type: String,
        },
        amount_due: {
            type: Number,
        },
        amount_paid: {
            type: Number,
        },
        amount_currency: {
            type: String,
        },
        description: {
            type: String,
        },
        invoice_pdf: {
            type: String,
        },
        storage_request_id: {
            type: String,
        },
        metadata: {
            type: mongoose.Schema.Types.Mixed,
        },
        company: companySchema,
        is_subscription: {
            type: Boolean,
            default: false,
        },
        status: {
            type: String,
        },
        total: {
            type: Number,
        },
        gateway:{
            type: String,
            enum: ['RAZORPAY', 'STRIPE'],
        }
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const invoice = mongoose.model('invoice', schema, 'invoice');

module.exports = invoice;
