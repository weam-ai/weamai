const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS, JOB_TYPE } = require('../config/constants/common');
mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };
const { countrySchema } = require('../utils/commonSchema');
const { COLLECTION_REF_UPDATE } = require('../config/constants/schemaref');
const { createJob } = require('../jobs');

const schema = new mongoose.Schema(
    {
        nm: {
            type: String,
        },
        code: {
            type: String,
        },
        country: {
            ...countrySchema
        },
        isActive: {
            type: Boolean,
            default: true
        },
        createdBy: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'user',
        },
        updatedBy: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'user',
        },
        deletedAt: {
            type: Date,
        },
        deletedBy: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'user',
        },
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

schema.post(['findOneAndUpdate', 'updateOne'], async function (doc) {
    if (doc) {
        const updatedData = await this.model.findOne(this.getQuery());
        if (updatedData)
            await createJob(JOB_TYPE.UPDATE_DBREF, { collectionDetails: COLLECTION_REF_UPDATE.STATE, updatedData: updatedData._doc });
    }
});

schema.pre(['findOneAndDelete', 'deleteOne'], async function (doc) {
    if (doc) {
        const deleteData = await this.model.findOne(this.getQuery());
        if (deleteData)
            await createJob(JOB_TYPE.DELETE_DBREF, { collectionDetails: COLLECTION_REF_UPDATE.STATE, removeData: deleteData._doc });
    }
});

const state = mongoose.model('state', schema, 'state');

module.exports = state;
