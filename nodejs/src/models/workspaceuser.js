const { Schema, model } = require('mongoose');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
const { userSchema } = require('../utils/commonSchema');

mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };

const schema = new Schema(
    {
        workspaceId: {
            type: Schema.Types.ObjectId,
            ref: 'workspace'
        },
        companyId: {
            type: Schema.Types.ObjectId,
            ref: 'company'
        },
        user: userSchema,
        userId:{
            type:Schema.Types.ObjectId,
            ref:"user"
        },
        teamId:{
            type: Schema.Types.ObjectId,
            ref: "teamUser"
        },
        role: {
            type: String
        },
    },
    {
        timestamps: true,
    },
);

schema.plugin(mongoosePaginate);

const workspaceuser = model('workspaceuser', schema, 'workspaceuser');

module.exports = workspaceuser;
