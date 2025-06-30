const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { userSchema, brainSchema } = require('../utils/commonSchema');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');


mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        title: {
            type: String,
        },
        user: userSchema,
        brain: brainSchema,
        isNewChat: {
            type: Boolean, // when new chat button click if flag is true then don't create new document 
        },
        isShare: {
            type: Boolean,
            default: false
        },
        isFork: {
            type: Boolean
        },
        teams:[{
            type: Schema.Types.ObjectId,
            ref: 'teamUser'
        }],
        deletedAt: { type: Date }
    },
    { timestamps: true },
);

schema.pre(/^find/, function (next) {
   
    this.populate({
        path: 'teams',
        model: 'teamUser', 
        select: 'teamName teamUsers', 
    });
    next();
});

schema.plugin(mongoosePaginate);

const chat = model('chat', schema, 'chat');

module.exports = chat;