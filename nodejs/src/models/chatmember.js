const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { userSchema, brainSchema } = require('../utils/commonSchema');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        chatId: {
            type: Schema.Types.ObjectId,
            ref: 'chat',
            index: true
        },
        title: {
            type: String,
        },
        user: userSchema,
        brain: brainSchema,
        isFavourite: {
            type: Boolean,
            default: false
        },
        isNewChat: {
            type: Boolean,
            default: true
        },
        invitedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user'
        },
        deletedAt: {
            type: Date
        },
        teamId:{
            type: Schema.Types.ObjectId,
            ref: 'teamUser' 
        }
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const chatmember = model('chatmember', schema, 'chatmember');

module.exports = chatmember;