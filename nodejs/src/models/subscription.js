const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { companySchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;

const schema = new Schema(
    {
        status: {
            type: String, 
            default: 'pending'
        },
        subscriptionId: {
            type: String
        },
        customerId: {
            type: String
        },
        plan: {
            type: String, // 1 Basic 2 Pro 3 Premium
        },
        planName: {
            type: String
        },
        gateway: {
            type: String
        },
        paymentMethod: {
            type: String
        },
        allowuser: {
            type: Number
        },
        vacantUser: {
            type: Number
        },
        startDate: {
            type: Date,
        },
        endDate: {
            type: Date,
        },
        cancel_at: {
            type: Date,
        },
        cancellation_reason: {
            type: String,
        },
        company: companySchema,
        isActive: {
            type: Boolean,
            default: true,
        },
        lastPaymentId: {
            type: String
        },
        notes: {
            type: Object
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
        unCancelAt: { type: Date },
        deletedAt: { type: Date },
        cancelAt: { type: Date },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const subscription = mongoose.model('subscription', schema, 'subscription');

module.exports = subscription;
