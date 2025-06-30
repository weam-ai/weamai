const Country = require('../models/country');
const dbService = require('../utils/dbService');

const addCountry = async (req) => {
    try {
        const existingCountry = await dbService.getDocumentByQuery(Country, { code: req.body.code });
        if (existingCountry) {
            throw new Error(_localize('module.alreadyExists', req, 'country'));
        }
        return dbService.createDocument(Country, req.body);
    } catch (error) {
        handleError(error, 'Error in addCountry');
    }
}

const checkCountry = async (req) => {
    const result = await Country.findById({ _id: req.params.id });
    if (!result) {
        throw new Error(_localize('module.notFound', req, 'country'));
    }
    return result;
}

const updateCountry = async (req) => {
    try {
        const existingCountry = await checkCountry(req);
        return dbService.findOneAndUpdateDocument(Country, { _id: req.params.id }, req.body);
    } catch (error) {
        handleError(error, 'Error in updateCountry');
    }
}

const viewCountry = async (req) => {
    try {
        const existingCountry = await checkCountry(req);
        return existingCountry;
    } catch (error) {
        handleError(error, 'Error in viewCountry');
    }
}

const deleteCountry = async (req) => {
    try {
        const existingCountry = await checkCountry(req);
        return Country.deleteOne({ _id: req.params.id });
    } catch (error) {
        handleError(error, 'Error in deleteCountry');
    }
}

const getAll = async (req) => {
    try {
        return dbService.getAllDocuments(Country, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error in getAll country');
    }
}

const partialUpdate = async (req) => {
    try {
        return Country.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).select('isActive');
    } catch (error) {
        handleError(error, 'Error in partailUpdate country');
    }
}

module.exports = {
    addCountry,
    viewCountry,
    updateCountry,
    deleteCountry,
    getAll,
    partialUpdate
}