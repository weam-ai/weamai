const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };
const Schema = mongoose.Schema;
const schema = new Schema(
    {
        route_name: {
            type: String,
            required: true,
            unique: true,
        },
        description: {
            type: String,
        },
        module: {
            type: String,
            required: true,
        },
        uri: {
            type: String,
            required: true,
        },
        createdBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },

        updatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
    },
    {
        timestamps: {
            createdAt: 'createdAt',
            updatedAt: 'updatedAt',
        },
        toJSON: { virtuals: true },
    },
);

schema.plugin(mongoosePaginate);

const permission = mongoose.model('permission', schema, 'permission');

module.exports = permission;