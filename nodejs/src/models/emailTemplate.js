const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;
const schema = new Schema(
    {
        nm: {
            type: String,
        },
        code: {
            type: String,
            unique: true,
        },
        subject: {
            type: String,
        },
        body: {
            type: String,
        },
        htmlPath: {
            type: String,
        },
        cssPath: {
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
schema.pre('save', async function (next) {
    this.isActive = true;
    next();
});

schema.plugin(mongoosePaginate);

const emailTemplate = mongoose.model('emailTemplate', schema, 'emailTemplate');

module.exports = emailTemplate;
