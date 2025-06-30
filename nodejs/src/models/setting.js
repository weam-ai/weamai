const mongoose = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new mongoose.Schema(
    {
        name: { type: String },
        code: { type: String },
        url: { type: String },
        details: { type: mongoose.Schema.Types.Mixed },
        isActive: { type: Boolean },
        deletedAt: { type: Date },
        deletedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'user' },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const setting = mongoose.model('setting', schema, 'setting');

module.exports = setting;
