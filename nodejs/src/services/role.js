const Role = require('../models/role');
const dbService = require('../utils/dbService');

const addRole = async (req) => {
    try {
        const existingRole = await dbService.getDocumentByQuery(Role, { code: req.body.code });
        if (existingRole) {
            throw new Error(_localize('module.alreadyExists', req, 'role'))
        }
        return dbService.createDocument(Role, req.body);
    } catch (error) {
        handleError(error, 'Error in admin add role service');
    }
}

const checkExistingRole = async (req) => {
    try {
        return Role.findById({ _id: req.params.id })
    } catch (error) {
        handleError(error, 'Error in checkExistingRole role service');
    }
}

const updateRole = async (req) => {
    try {
        const existingRole = await checkExistingRole(req);
        if (!existingRole) {
            throw new Error(_localize('module.notFound', req, 'role'))
        }
        return dbService.findOneAndUpdateDocument(Role, { _id: req.params.id }, req.body)
    } catch (error) {
        handleError(error, 'Error in admin update role service');
    }
}

const getRole = async (req) => {
    try {
        const existingRole = await checkExistingRole(req);
        if (!existingRole) {
            throw new Error(_localize('module.notFound', req, 'role'))
        }
        return existingRole;
    } catch (error) {
        handleError(error, 'Error in admin get role service');
    }
}

const deleteRole = async (req) => {
    try {
        const existingRole = await checkExistingRole(req);
        if (!existingRole) {
            throw new Error(_localize('module.notFound', req, 'role'))
        }
        return dbService.deleteDocument(Role, { _id: req.params.id });
    } catch (error) {
        handleError(error, 'Error in admin delete role service');
    }
}

const getAllRole = async (req) => {
    try {
        return dbService.getAllDocuments(Role, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error in admin  getall role service');
    }
}

const partialUpdate = async (req) => {
    try {
        return Role.findByIdAndUpdate({ _id: req.params.id }, req.body, { new: true }).select('isActive');
    } catch (error) {
        handleError(error, 'Error - partialUpdate');
    }
}

module.exports = {
    addRole,
    updateRole,
    deleteRole,
    getAllRole,
    getRole,
    partialUpdate
}