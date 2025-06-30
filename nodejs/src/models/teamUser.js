const mongoose = require("mongoose");
const { userSchema } = require("../utils/commonSchema");
const mongoosePaginate = require('mongoose-paginate-v2');
const { JOB_TYPE } = require("../config/constants/common");
const { COLLECTION_REF_UPDATE } = require("../config/constants/schemaref");
const { createJob } = require("../jobs");


const teamUserSchema = new mongoose.Schema({
    teamName: {
        type: String,
        required: true
    },
    companyId: {
        type:String,
        required:true
    },
    teamUsers: [userSchema ],
    updatedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'user',
    },
}, { timestamps: true })

teamUserSchema.plugin(mongoosePaginate);


teamUserSchema.post(['findOneAndUpdate', 'updateOne'], async function (doc) {
    if (doc) {
        const updatedData = await this.model.findOne(this.getQuery());
        if (updatedData)
            await createJob(JOB_TYPE.UPDATE_DBREF, { collectionDetails: COLLECTION_REF_UPDATE.TEAMUSER, updatedData: updatedData._doc });
    }
});

teamUserSchema.pre(['findOneAndDelete', 'deleteOne'], async function(doc) {
    if (doc) {
        const deleteData = await this.model.findOne(this.getQuery());
        if (deleteData)
            await createJob(JOB_TYPE.DELETE_DBREF, { collectionDetails: COLLECTION_REF_UPDATE.TEAMUSER, removeData: deleteData._doc })
    } 
})


const teamUser=mongoose.model('teamUser',teamUserSchema,"teamUser")

module.exports=teamUser