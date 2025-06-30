const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS, STORAGE_REQUEST_STATUS } = require('../config/constants/common');
const { companySchema, userSchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };
const Schema = mongoose.Schema;

const schema = new Schema({
    user: userSchema,
    company: companySchema,
    requestSize: { 
        type: Number, 
        required: true 
    }, // Size in MB
    status: { 
        type: String, 
        default: STORAGE_REQUEST_STATUS.PENDING 
    },
    createdAt: { 
        type: Date, 
        default: Date.now 
    }
}, {
    timestamps: true
});

schema.plugin(mongoosePaginate);

const storagerequest = mongoose.model('storagerequest', schema, 'storagerequest');

module.exports = storagerequest;