const mongoose = require('../config/db');
const mongoosePaginate = require('mongoose-paginate-v2');
const { CUSTOM_PAGINATE_LABELS } = require('../config/constants/common');
mongoosePaginate.paginate.options = { customLabels: CUSTOM_PAGINATE_LABELS };
const Schema = mongoose.Schema;
const { companySchema, botSchema } = require('../utils/commonSchema');

// this schema required for python api to fetch query data
const extraConfigSchema = {
    extraConfig: {
        frequencyPenalty: {
            type: Number,
        },
        logitBias: {},
        logprobs: { type: Boolean },
        topLogprobs: {
            type: Number,
        },
        maxTokens: {
            type: Number,
        },
        presencePenalty: {
            type: Number,
        },
        responseFormat: {},
        seed: {
            type: Number,
        },
        stop: [],
        stream: { type: Boolean },
        streamOptions: {},
        temperature: { type: Number, default: 0.7 },
        topP: {
            type: Number,
        },
        tools: [],
        toolChoice: {
            type: String,
        },
        user: {
            type: String,
        },
        // hugging face config
        sample: { type: Boolean },
        topK: { type: Number },
        typicalP: { type: Number },
        repetitionPenalty: { type: Number },
        stopSequences: { type: [String] },
        numInference: { type: Number },
        gScale: { type: Number }
    },
};

const huggingFaceConfig = {
    taskType: { type: String },
    apiType: { type: String },
    description: { type: String },
    repo: { type: String },
    context: { type: Number },
    endpoint: { type: String },
    visionEnable: { type: Boolean }
}

const schema = new Schema(
    {
        name: {
            type: String
        },
        bot: botSchema,
        company: companySchema,
        config: {
            apikey: {
                type: String
            },
            ...huggingFaceConfig
        },
        modelType: {
            type: Number, // 1 for embedding 2 for chat
        },
        dimensions: { type: Number }, // for text embadding model
        isActive: {
            type: Boolean,
            default: true
        },
        stream: {
            type: Boolean, // model support streaming
        },
        tool: {
            type: Boolean, // model support tooling
        },
        provider: {
            type: String,
        },
        createdBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        updatedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        deletedBy: {
            type: Schema.Types.ObjectId,
            ref: 'user',
        },
        deletedAt: { type: Date },
        ...extraConfigSchema
    },
    { timestamps: true },
);

schema.plugin(mongoosePaginate);

const companymodel = mongoose.model('companymodel', schema, 'companymodel');

module.exports = companymodel;
