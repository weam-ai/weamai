const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { userSchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        user: userSchema,
        itemId: {
            type: Schema.Types.ObjectId,
            required: true,
            index: true
        },
        type: {
            type: String,
            enum: ['prompt', 'doc', 'customgpt', 'chat'],
            required: true
        },
        companyId: {
            type: Schema.Types.ObjectId,
            ref: 'company',
            index: true
        }
    },
    { timestamps: true }
);

schema.plugin(mongoosePaginate);
const bookmark = model('bookmark', schema, 'bookmarks');

module.exports = bookmark; 