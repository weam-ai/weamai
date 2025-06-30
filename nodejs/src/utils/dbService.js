const { getFilterQuery } = require('../utils/helper');
const excel = require('exceljs');
const Company = require('../models/company');
/*
 * createDocument : create any mongoose document
 * @param  model  : mongoose model
 * @param  data   : {}
 */

const createDocument = async (model, data) => {
    try {
        return model.create(data);
    } catch (err) {
        throw err;
    }
};

/*
 * deleteDocument : delete any existing mongoose document
 * @param  model  : mongoose model
 * @param  id     : mongoose document's _id
 */

const deleteDocument = async (model, filter) => {
    try {
        return model.deleteOne(filter);
    } catch (err) {
        throw err;
    }
};

/*
 * getAllDocuments : find all the mongoose document
 * @param  model   : mongoose model
 * @param query    : {}
 * @param options  : {}
 */

const getAllDocuments = async (model, query, options, softDelete = true) => {
    try {
        query = await getFilterQuery(query);
        if (softDelete) query.deletedAt = { $exists: false };            
        return model.paginate(query, options);
    } catch (err) {
        throw err;
    }
};

/*
 * getSingleDocumentById : find single mongoose document
 * @param  model  : mongoose model
 * @param  id     : mongoose document's _id
 * @param  select : [] *optional
 */

const getSingleDocumentById = async (model, id, select = [],companyId) => {
    try {
        if(companyId){
            const company = await Company.findOne({ _id: companyId },{ countryName: 1, countryCode: 1 });
            return { ...await model.findById({ _id: id }, select).lean(), countryName: company.countryName, countryCode: company.countryCode };
        }
        return model.findById({ _id: id }, select);
    } catch (err) {
        throw err;
    }
};

/*
 * bulkInsert     : create document in bulk mongoose document
 * @param  model  : mongoose model
 * @param  data   : {}
 */

const bulkInsert = async (model, data) => {
    try {
        const result = await model.insertMany(data);
        if (result !== undefined && result.length > 0) {
            return result;
        }
        return false;
    } catch (err) {
        throw err;
    }
};

/*
 * bulkInsert     : update existing document in bulk mongoose document
 * @param  model  : mongoose model
 * @param  filter : {}
 * @param  data   : {}
 */

const bulkUpdate = async (model, filter, data) => {
    try {
        const result = await model.updateMany(filter, data);
        if (result !== undefined) {
            return result;
        }
        return false;
    } catch (err) {
        throw err;
    }
};

/*
 * getDocumentByQuery : find document by dynamic query
 * @param  model      : mongoose model
 * @param  where      : {}
 * @param  select     : [] *optional
 */
const getDocumentByQuery = async (model, where, select = [], options = {}) => {
    try {
        const data = await model.findOne(where, select, options).lean();
        return data;
    } catch (err) {
        throw err;
    }
};

/*
 * findOneAndUpdateDocument : find existing document and update mongoose document
 * @param  model   : mongoose model
 * @param  filter  : {}
 * @param  data    : {}
 * @param  options : {} *optional
 */

const findOneAndUpdateDocument = async (model, filter, data, options = { new: true }, populate = [],) => {
    try {
        const result = await model
            .findOneAndUpdate(filter, data, options)
            .populate(populate);
        return result;
    } catch (err) {
        throw err;
    }
};

/*
 * findOneAndDeleteDocument : find existing document and delete mongoose document
 * @param  model  : mongoose model
 * @param  filter  : {}
 * @param  options : {} *optional
 */

const findOneAndDeleteDocument = async (model, filter, options = {}) => {
    try {
        return model.findOneAndDelete(filter, options);
    } catch (err) {
        throw err;
    }
};

const exportToExcel = (sheetName, columns, data) => {
    try {
        const workbook = new excel.Workbook();
        const worksheet = workbook.addWorksheet(sheetName);
        worksheet.columns = columns;
        worksheet.columns.forEach((column) => {
            column.width =
                column.header.length < 12 ? 12 : column.header.length;
        });
        worksheet.getRow(1).font = { bold: true };
        worksheet.addRows(data);
        return workbook;
    } catch (err) {
        throw err;
    }
};

const dbHooks = async (modelSchema) => {
    modelSchema.pre(
        ['findOne', 'find', 'updateOne', 'updateMany'],
        function (next) {
            this.getQuery().deletedAt = { $exists: false };
            next();
        },
    );
};

module.exports = {
    createDocument,
    getAllDocuments,
    deleteDocument,
    getSingleDocumentById,
    bulkInsert,
    bulkUpdate,
    getDocumentByQuery,
    findOneAndUpdateDocument,
    findOneAndDeleteDocument,
    exportToExcel,
    dbHooks,
};