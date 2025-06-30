
const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');

const schema = new Schema(
    {
        brainId: {
            type: Schema.Types.ObjectId,
            ref: 'brain'
        },
        chatId: {
            type: Schema.Types.ObjectId,
            ref: 'chat'
        },
        access: { type: Number }, // 1 for public 2 for private
        permission: {
            type: String
        },
        uri: {
            type: String
        },
        conversation: [],
        shareBy: {
            type: Schema.Types.ObjectId,
            ref: 'user'
        },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const shareChat = model('shareChat', schema, 'shareChat');

module.exports = shareChat;
