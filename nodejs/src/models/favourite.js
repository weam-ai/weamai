const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        username: {
            type: String,
        },
        userId: {
            type: Schema.Types.ObjectId,
            ref: 'user',
            index: true
        },
        threadId: {
            type: Schema.Types.ObjectId,
            ref: 'thread',
            index: true
        },
        threadMsg: {
            type: String,
        },
        aiResponse: {
            type: String,
        },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const favourite = model('favourite', schema, 'favourite');

module.exports = favourite;
