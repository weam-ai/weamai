const State = require('../models/state');
const dbService = require('../utils/dbService');

const addState = async (req) => {
    try {
        const existingState = await dbService.getDocumentByQuery(State, { code: req.body.code });
        if (existingState) {
            throw new Error(_localize('module.alreadyExists', req, 'state'));
        }
        return dbService.createDocument(State, req.body);
    } catch (error) {
        handleError(error, 'Error in addState');
    }
}

const checkState = async (req) => {
    const result = await State.findById({ _id: req.params.id });
    if (!result) {
        throw new Error(_localize('module.notFound', req, 'state'));
    }
    return result;
}

const updateState = async (req) => {
    try {
        await checkState(req);
        return dbService.findOneAndUpdateDocument(State, { _id: req.params.id }, req.body);
    } catch (error) {
        handleError(error, 'Error in updateState');
    }
}

const viewState = async (req) => {
    try {
        const existingState = await checkState(req);
        return existingState;
    } catch (error) {
        handleError(error, 'Error in viewState');
    }
}

const deleteState = async (req) => {
    try {
        await checkState(req);
        return State.deleteOne({ _id: req.params.id });
    } catch (error) {
        handleError(error, 'Error in deleteState');
    }
}

const getAll = async (req) => {
    try {
        return dbService.getAllDocuments(State, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error in getAll state');
    }
}

const partialUpdate = async (req) => {
    try {
        return State.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).select('isActive');
    } catch (error) {
        handleError(error, 'Error in partailUpdate state');
    }
}

module.exports = {
    addState,
    updateState,
    viewState,
    deleteState,
    getAll,
    partialUpdate
}