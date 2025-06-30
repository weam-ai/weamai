const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { userSchema, fileSchema, companySchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        
        chatId: {
            type: Schema.Types.ObjectId,
            ref: 'chat'
        },
        fileId: {
            type: Schema.Types.ObjectId,
            ref: 'file'
        },
        userId: {
            type: Schema.Types.ObjectId,
            ref: 'user'
        },
        brainId: {
            type: Schema.Types.ObjectId,
            ref: 'brain'
        },
        embedding_api_key: {
            type: Schema.Types.ObjectId,
            ref: 'companymodel'
        },
        company: companySchema,
        doc: fileSchema,
        docShare: [userSchema],
        isShare: {
            type: Boolean,
            default: false,
        },
        isActive: {
            type: Boolean,
            default: true,
        },
        favoriteByUsers: [{
            type: Schema.Types.ObjectId,
            ref: 'users'
        }],
     },
    { timestamps: true },
);


schema.plugin(mongoosePaginate);

const chatdocs = model('chatdocs', schema, 'chatdocs');

module.exports = chatdocs;
