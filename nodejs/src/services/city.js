const City = require('../models/city');
const dbService = require('../utils/dbService');

const addCity = async (req) => {
    try {
        const existingCity = await dbService.getDocumentByQuery(City, { code: req.body.code });
        if (existingCity) {
            throw new Error(_localize('module.alreadyExists', req, 'city'));
        }
        return dbService.createDocument(City, req.body);
    } catch (error) {
        handleError(error, 'Error in addCity');
    }
}

const checkCity = async (req) => {
    const result = await City.findById({ _id: req.params.id });
    if (!result) {
        throw new Error(_localize('module.notFound', req, 'city'));
    }
    return result;
}

const updateCity = async (req) => {
    try {
        await checkCity(req);
        return dbService.findOneAndUpdateDocument(City, { _id: req.params.id }, req.body);
    } catch (error) {
        handleError(error, 'Error in updateCity');
    }
}

const viewCity = async (req) => {
    try {
        const existingState = await checkCity(req);
        return existingState;
    } catch (error) {
        handleError(error, 'Error in viewCity');
    }
}

const deleteCity = async (req) => {
    try {
        await checkCity(req);
        return City.deleteOne({ _id: req.params.id });
    } catch (error) {
        handleError(error, 'Error in deleteCity');
    }
}

const getAll = async (req) => {
    try {
        return dbService.getAllDocuments(City, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error in getAll city');
    }
}

const partialUpdate = async (req) => {
    try {
        return City.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).select('isActive');
    } catch (error) {
        handleError(error, 'Error in partailUpdate city');
    }
}

module.exports = {
    addCity,
    updateCity,
    viewCity,
    deleteCity,
    getAll,
    partialUpdate
}