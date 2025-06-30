const mongoose = require('mongoose');

const fileSchema =  {
    name: {
        type: String
    },
    uri: {
        type: String,
    },
    mime_type: {
        type: String,
    },
    file_size: {
        type: String,
    },
    createdAt: {
        type: Date
    },
    id: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'file',
        index: true
    }
};

module.exports = {
    userSchema: {
        email: {
            type: String
        },
        fname: {
            type: String
        },
        lname: {
            type: String
        },
        profile: fileSchema,
        id: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'user',
            index: true
        }
    },
    teamSchema:{
        teamName:{
            type:String
        },
        id:{
            type: mongoose.Schema.Types.ObjectId,
            ref: 'teamUser',
            index: true
        }
    },
    countrySchema: {
        nm: {
            type: String,
        },
        code: {
            type: String,
        },
        id: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'country',
            index: true
        }
    },
    stateSchema: {
        nm: {
            type: String,
        },
        code: {
            type: String,
        },
        id: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'state',
            index: true
        }
    },
    citySchema: {
        nm: {
            type: String
        },
        code: {
            type: String
        },
        id: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'city',
            index: true
        }
    },
    fileSchema: fileSchema,
    companySchema: {
        name: {
            type: String
        },
        slug: {
            type: String
        },
        id: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'company',
            index: true
        }
    },
    botSchema: {
        title: {
            type: String,
        },
        code: {
            type: String
        },
        id: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'bot',
            index: true
        }
    },
    brainSchema: {
        title: {
            type: String,
        },
        slug: {
            type: String,
        },
        id: {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'brain',
            index: true
        }        
    }
}