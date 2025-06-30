const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { companySchema, teamSchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        title: {
            type: String,
        },
        slug: {
            type: String,
            index: true,
        },
        company: companySchema,
        isActive: {
            type: Boolean,
            default: true
        },
        createdBy:{
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        isDefault: {
            type: Boolean,
            default: false
        },
        deletedAt: {
            type: Date,
        },
        teams:[teamSchema]
    },
    {
        timestamps: true,
    },
);

// Compound unique index on slug and company.id 
schema.index({ slug: 1, 'company.id': 1 }, { unique: true });

// Ensure that slug is unique per company
schema.pre('save', async function (next) {
    if (this.isModified('slug')) {
        // Check if there is any other document with the same slug for the same company
        const count = await this.constructor.countDocuments({
            slug: this.slug,
            'company.id': this.company.id
        });
        if (count > 0) {
            const error = new Error('This workspace already exists')
            return next(error);
        }
    }
    next();
});

schema.post(/^find/, async function (docs) {
    if (docs) {
       
        const docsArray = Array.isArray(docs) ? docs : [docs];

       
        await this.model.populate(docsArray, {
            path: 'teams.id',
            model: 'teamUser', 
        });

        
    }
});


schema.plugin(mongoosePaginate);

const workspace = model('workspace', schema, 'workspace');

module.exports = workspace;
