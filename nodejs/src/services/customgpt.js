const CustomGpt = require('../models/customgpt');
const { formatUser, formatDBFileData, formatBrain, getCompanyId } = require('../utils/helper');
const dbService = require('../utils/dbService');
const CompanyModal = require('../models/userBot');
const File = require('../models/file');
const { LINK, API } = require('../config/config');
const { JWT_STRING } = require('../config/constants/common');
const ChatDocs = require('../models/chatdocs');
// const { removeExistingDocument, removeExistingImage, fileData } = require('./uploadFile');
const Brain = require('../models/brains');
const ShareBrain = require('../models/shareBrain');
const { accessOfBrainToUser } = require('./common');
const { extractAuthToken } = require('./company');
const { MODAL_NAME } = require('../config/constants/aimodal');
const { getShareBrains, getBrainStatus } = require('./brain');
const commonSchema = require('../utils/commonSchema');

function chatDocsFileFormat(file) {
    return {
        name: file.name,
        uri: file.uri,
        mime_type: file.mime_type,
        file_size: file.file_size,
        createdAt: file.createdAt
    }
}

async function createChatDocs(payload) {
    ChatDocs.create(payload);
}

const addCustomGpt = async (req) => {
    try {
        const { fileData } = require('./uploadFile');
        const { title, brain, responseModel, goals: reqGoals, instructions: reqInstructions } = req.body;
        const { id: brainId } = brain;
        const { company } = responseModel;

        const slug = slugify(title);
        const createData = { ...req.body, slug, coverImg: {}, doc: [] }; 

        const existing = await CustomGpt.findOne({ slug, 'brain.id': brainId });
        if (existing) throw new Error(_localize('module.alreadyExists', req, 'custom gpt'));

        if (req.files['coverImg']) {
            const coverFile = await File.create(fileData(req.files['coverImg'][0]));
            createData['coverImg'] = formatDBFileData(coverFile);
        }

        if (req.files?.doc?.length > 0) {
            const defaultEmbedding = await CompanyModal.findOne({ 'company.id': company.id, name: 'text-embedding-3-small' });

          const docFile = await File.insertMany(
            req.files["doc"].map((file) => fileData(file))
          );

          // Create chat docs in bulk instead of individual operations
            ChatDocs.insertMany(docFile.map(dfile => ({
              userId: req.userId,
              fileId: dfile._id,
              brainId,
              doc: chatDocsFileFormat(dfile),
            })));

            const vectorData = docFile.map(file => ({
            type: file.type,
            companyId: company.id,
            fileId: file.id,
            api_key_id: defaultEmbedding._id.toString(),
                tag: file.uri.split('/')[2],
            uri: file.uri,
            brainId,
                file_name: file.name
          }));

          storeVectorData(req, vectorData);

            createData['doc'] = docFile.map(file => formatDBFileData(file));
            createData['embedding_model'] = {
            name: defaultEmbedding.name,
            company: defaultEmbedding.company,
            id: defaultEmbedding._id,
          };
        }

        const goals = JSON.parse(reqGoals) || [];
        const instructions = [];
        if (reqInstructions) {
            for (let instruction of JSON.parse(reqInstructions)) {
                if (instruction.trim() !== '')
                    instructions.push(instruction.trim().replace(/\s+/g, ' '));
            }
        }

        return CustomGpt.create({
            ...createData,
            goals,
            instructions,
            owner: formatUser(req.user),
        });

    } catch (error) {
        handleError(error, 'Error - addCustomGpt');
    }
};

const updateCustomGpt = async (req) => {
    try {
        const { removeExistingDocument, removeExistingImage, fileData } = require('./uploadFile');
        const existingBot = await CustomGpt.findById({ _id: req.params.id }, { doc: 1, coverImg: 1, brain: 1 });
        
        if (!existingBot) throw new Error(_localize('module.notFound', req, 'custom bot'));
        let instructions = [];

        const { title, responseModel, goals: reqGoals, instructions: reqInstructions,brain } = req.body;
        const { company } = responseModel;

        let updateBody = {
            ...req.body,
            slug: slugify(title),
        }


        if (reqGoals) {
            Object.assign(updateBody, { goals: JSON.parse(reqGoals) || [] })
        }
        if (reqInstructions) {
            for (let instruction of JSON.parse(reqInstructions)) {
                if (instruction.trim() !== '')
                    instructions.push(instruction.trim().replace(/\s+/g, ' '));
            }
            Object.assign(updateBody, { instructions })
        }

        if (req.files['coverImg']) {
            // if user upload new image then old image remove from db and s3
            const previousImg = !!existingBot?.coverImg?.id;
            if (previousImg) removeExistingImage(existingBot.coverImg.id, existingBot.coverImg.uri);
            //TODO : If new Image request delete older image
            const [coverFile] = await Promise.all([
                File.create(fileData(req.files['coverImg'][0])),
            ]);
            Object.assign(updateBody, { coverImg: formatDBFileData(coverFile) })
        }
        //if coverImg is null then remove coverImg get from existingBot and call removeExistingImage
        if (!req.files['coverImg']) {
            if (existingBot?.coverImg?.id) removeExistingImage(existingBot.coverImg.id, existingBot.coverImg.uri);
        }

        const previousDocs = existingBot?.doc || [];
        let filteredPreviousDocs  = previousDocs;
        
        if (req.body.removeDoc) {
            const removeDoc = JSON.parse(req.body.removeDoc);
            
            removeDoc.forEach(doc => {
                if (doc?.id && doc?.uri) {
                    removeExistingDocument(doc.id, doc.uri);
                }
            });
            // Create a Set of IDs from the removeArray for quick lookup
            const removeSet = new Set(removeDoc.map(item => item.id));
            // Filter the existingArray to exclude items present in the removeSet
            filteredPreviousDocs = previousDocs.filter(existingItem => {
                return !removeSet.has(existingItem.id.toString());
            });
        }
        
        if (req?.files?.doc?.length > 0) {
            // if user uploads new documents, remove all old documents from db and s3
            
            // if (previousDocs.length > 0) {
            //     previousDocs.forEach(doc => {
            //         if (doc?.id && doc?.uri) {
            //             removeExistingDocument(doc.id, doc.uri);
            //         }
            //     });
            // }
            
            const docFile = await File.insertMany(
                req.files['doc'].map(file => fileData(file))
            );

            // Create chat docs in bulk instead of individual operations
            ChatDocs.insertMany(docFile.map(dfile => ({
                userId: req.userId,
                fileId: dfile._id,
                brainId: existingBot.brain.id,
                doc: chatDocsFileFormat(dfile),
            })));

            // default text embadding modal for text
            const defaultEmbedding = await CompanyModal.findOne({ 'company.id': company.id, name: 'text-embedding-3-small' });

            updateBody['doc'] = docFile.map(file => formatDBFileData(file));
            updateBody['embedding_model'] = {
                name: defaultEmbedding.name,
                company: defaultEmbedding.company,
                id: defaultEmbedding._id,
            };
            
            const vectorData = docFile.map(file => ({
                type: file.type,
                companyId: company.id,
                fileId: file.id,
                api_key_id: defaultEmbedding._id.toString(),
                tag: file.uri.split('/')[2],
                uri: file.uri,
                brainId: existingBot.brain.id.toString(),
                file_name: file.name
            }));
 
            // Store vector data
            storeVectorData(req, vectorData);
            const newDocs = docFile.map(file => formatDBFileData(file));
            Object.assign(updateBody, { doc: [...filteredPreviousDocs, ...newDocs] });            
        } else {
            Object.assign(updateBody, { doc: filteredPreviousDocs })
        }

        

        return CustomGpt.findByIdAndUpdate({ _id: req.params.id }, updateBody, { new: true });
    } catch (error) {
        handleError(error, 'Error - updateCustomGpt');
    }
}

const viewCustomGpt = async (req) => {
    try {
        return CustomGpt.findById({ _id: req.params.id } );
    } catch (error) {
        handleError(error, 'Error - viewCustomGpt');
    }
}

const deleteCustomGpt = async (req) => {
    try {  
        return CustomGpt.deleteOne({ _id: req.params.id });
    } catch (error) {
        handleError(error, 'Error - deleteCustomGpt');
    }
}

const getAll = async (req) => {
    try {

        const {isPrivateBrainVisible}=req.user

        if(req.body.query["brain.id"]){

            const accessShareBrain=await ShareBrain.findOne({"brain.id":req.body.query["brain.id"],"user.id":req.user.id})

            if(!accessShareBrain){
                return {
                    status: 302,
                    message: "You are unauthorized to access this custom bots",
                };
            }

            const currBrain=await Brain.findById({ _id:req.body.query["brain.id"]})

            if(!isPrivateBrainVisible && !currBrain.isShare){
               return {
                   status: 302,
                   message: "You are unauthorized to access this custom bots",
               };
            }
        }
    
        return dbService.getAllDocuments(
            CustomGpt,
            req.body.query || {},
            req.body.options || {},
        )
    } catch (error) {
        handleError(error, 'Error - getAll');
    }
}

const partialUpdate = async (req) => {
    try {
        return CustomGpt.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).select('isActive');
    } catch (error) {
        handleError(error, 'Error - partialUpdate');
    }
}

const storeVectorData = async (req, payloads) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000);
    try {
        const token = extractAuthToken(req);
        
        const jsonPayload = payloads.map(payload => ({
            file_type: payload.type,
            source: 's3_url',
            file_url: payload.uri,
            page_wise: 'False',
            vector_index: payload.companyId.toString(),
            dimensions: 1536,
            id: payload.fileId.toString(),
            api_key_id: payload.api_key_id.toString(),
            tag: payload.uri.split('/')[2],
            company_id: payload.companyId.toString(),
            brain_id: payload.brainId,
            file_name: payload.file_name
        }));

        const response = await fetch(
            `${LINK.PYTHON_API_URL}/${API.PYTHON_API_PREFIX}/vector/openai-multi-store-vector`,
            {
                method: 'POST',
                body: JSON.stringify({'payload_list':jsonPayload}),
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `${JWT_STRING}${token}`,
                    Origin: LINK.FRONT_URL
                },
            }
        );
        logger.info(`openai store vector return ${response.status}`);
        if (response.ok) return true;
        return false;

    } catch (error) {
        handleError(error, 'Error - storeVectorData');
    } finally {
        clearTimeout(timeoutId);
    }

    // try {
    //     const token = extractAuthToken(req);
    //     const response = await fetch(
    //         `${LINK.PYTHON_API_URL}${API.PREFIX}/vector/openai-store-vector`,
    //         {
    //             method: 'POST',
    //             body: JSON.stringify({
    //                 file_type: payload.type,
    //                 source: 's3_url',
    //                 file_url: payload.uri,
    //                 page_wise: 'False',
    //                 vector_index: payload.companyId.toString(),
    //                 dimensions: 1536,
    //                 id: payload.fileId.toString(),
    //                 api_key_id: payload.api_key_id.toString(),
    //                 tag: payload.uri.split('/')[2],
    //                 company_id: payload.companyId.toString(),
    //                 brain_id: payload.brainId,
    //                 file_name: payload.file_name
    //             }),
    //             headers: {
    //                 'Content-Type': 'application/json',
    //                 Authorization: `${JWT_STRING}${token}`,
    //                 Origin: LINK.FRONT_URL
    //             },
    //         }
    //     );
    //     logger.info(`openai store vector return ${response.status}`);
    //     if (response.ok) return true;
    //     return false;

    // } catch (error) {
    //     handleError(error, 'Error - storeVectorData');
    // }
}

const assignDefaultGpt = async (req) => {
    try {
        let instructions = [];
        let goals = [];
        const { title, brain, responseModel : reqResponseModel, goals: reqgoals, instructions: reqInstructions, selectedBrain } = req.body;
        const {isPrivateBrainVisible}=req.user

        const bulk = [];
        
        
        const timestamp = Date.now(); 
        const slug = `${slugify(title)}-${timestamp}`;
        const createData = { ...req.body, slug, coverImg: {}, doc: [] }; 

        if (reqgoals) {
            for (let goal of JSON.parse(reqgoals)) {
                if (goal.trim() !== '')
                    goals.push(goal.trim().replace(/\s+/g, ' '));
            }
        }

        if (reqInstructions) {
            for (let instruction of JSON.parse(reqInstructions)) {
                if (instruction.trim() !== '')
                    instructions.push(instruction.trim().replace(/\s+/g, ' '));
            }
        }

        const defaultModal = await CompanyModal.findOne({ 'company.id': getCompanyId(req.user), name: MODAL_NAME.GPT_4_1 });
        if (!defaultModal) return false;
        
        responseModel = {
            name: defaultModal?.name,
            id: defaultModal?._id,
            company: reqResponseModel?.company,
            bot: defaultModal.bot
        }

        for (const br of selectedBrain) {
            const hasAccess = await accessOfBrainToUser({ brainId: br.id, userId: req.user.id });
            if (hasAccess &&  (br.isShare || (isPrivateBrainVisible && !br.isShare))) {
                
                bulk.push({
                    ...createData,
                    goals,
                    instructions,
                    brain: formatBrain(br),
                    owner: formatUser(req.user),
                    responseModel
                });
            }
        } 

        return CustomGpt.insertMany(bulk);
        
    } catch (error) {
        handleError(error, 'Error - addCustomGpt');
    }
}

async function usersWiseGetAll(req) {
    try {
        const brains = await getShareBrains(req);
        if (!brains.length) return { data: [], paginator: {} };
        const brainStatus = await getBrainStatus(brains);
        const query ={
            'brain.id': { $in: brains.map(ele => ele.brain.id) },
            ...req.body.query
        }
        delete query.workspaceId;
        const result = await dbService.getAllDocuments(CustomGpt, query, req.body.options || {});
        const finalResult = result.data.map((record) => ({
            ...record._doc,
            isShare: brainStatus.find((ele) => ele?._id?.toString() === record?.brain?.id?.toString())?.isShare,
        }))
        return {
            data: finalResult,
            paginator: result.paginator
        }
    } catch (error) {
        handleError(error, 'Error - usersWiseGetAll');
    }
}

const favoriteCustomGpt = async (req) => {
    try {
        const updateOperation = req.body.isFavorite
            ? { $addToSet: { favoriteByUsers: req.userId } }
            : { $pull: { favoriteByUsers: req.userId } };

        return await CustomGpt.findOneAndUpdate(
            { _id: req.params.id },
            updateOperation,
            { new: true }
        ).select("favoriteByUsers _id");
    } catch (error) {
        handleError(error, "Error - favoriteCustomGpt");
    }
};

module.exports = {
    addCustomGpt,
    updateCustomGpt,
    viewCustomGpt,
    deleteCustomGpt,
    getAll,
    partialUpdate,
    storeVectorData,
    assignDefaultGpt,
    usersWiseGetAll,
    favoriteCustomGpt
}