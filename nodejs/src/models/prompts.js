const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { brainSchema, userSchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        title: {
            type: String,
        },
        content: {
            type: String,
        },
        // user who created the brain
        user: userSchema,
        brain: brainSchema,
        isActive: {
            type: Boolean,
            default: false,
        },
        tags: [{ type: String }],
        website: [],
        summaries: { type: Schema.Types.Mixed },
        addinfo: {
            code: { type: String },
            label: { type: String },
            value: { type: String },
        },
        brandInfo: {
            name: { type: String },
            tagline: { type: String },
            mission: { type: String },
            values: { type: String },
            audience: { type: String },
            industry: { type: String },
            website: [],
            summaries: { type: Schema.Types.Mixed }
        },
        companyInfo: {
            name: { type: String },
            tagline: { type: String },
            overview: { type: String },
            mission: { type: String },
            values: { type: String },
            vision: { type: String },
            industry: { type: String },
            headquarter: { type: String },
            website: [],
            summaries: { type: Schema.Types.Mixed }
        },
        productInfo: {
            name: { type: String },
            description: { type: String },
            category: { type: String },
            usp: { type: String },
            market: { type: String },
            specification: { type: String },
            benifits: { type: String },
            usage: { type: String },
            skus: { type: String },
            website: [],
            summaries: { type: Schema.Types.Mixed }
        },
        isCompleted: { type: Boolean },
        defaultprompt: { 
            type: Boolean,
            default: false 
        },
        deletedAt: { type: Date },
        favoriteByUsers: [{
            type: Schema.Types.ObjectId,
            ref: 'users'
        }],
     },
    { timestamps: true },
);



schema.plugin(mongoosePaginate);

const prompts = model('prompts', schema, 'prompts');

module.exports = prompts;
