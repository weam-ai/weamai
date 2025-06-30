const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const Schema = mongoose.Schema;
const schema = new Schema(
    {
        name: {
            type: String,
            required: true,
        },

        code: {
            type: String,
            required: true,
            unique: true,
        },

        isActive: { type: Boolean, default: true },
        canDel: { type: Boolean, default: true },

        createdAt: { type: Date },

        updatedAt: { type: Date },

        createdBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },

        updatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },

        deletedAt: { type: Date },
    },
    {
        timestamps: {
            createdAt: 'createdAt',
            updatedAt: 'updatedAt',
        },
        toJSON: { virtuals: true },
    },
);

schema.virtual('permissions', {
    ref: 'permissionRole',
    localField: '_id',
    foreignField: 'role_id',
});

schema.plugin(mongoosePaginate);

const role = mongoose.model('role', schema, 'role');

module.exports = role;
