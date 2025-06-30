const Invoice = require('../models/invoice');
const dbService = require('../utils/dbService');

const createInvoiceFromEvent = async (event, userCompany) => {
    try {
        const metadata = JSON.stringify(event?.data?.object?.metadata);
        const storageRequestId = event?.data?.object?.metadata["Storage Request Id"];
        
        const data = {
            invoiceId: event?.data?.object?.id,
            invoiceNo: event?.data?.object?.number,
            interval: event?.data?.object?.interval,
            description: event?.data?.object?.description,
            email: event?.data?.object?.customer_email,
            amount_due: event?.data?.object?.amount_due,
            amount_paid: event?.data?.object?.amount_paid,
            invoice_pdf: event?.data?.object?.invoice_pdf || '',
            storage_request_id: storageRequestId,
            metadata: metadata,
            company: userCompany.company,
            is_subscription: event?.data?.object?.subscription ? true : false,
            status: event?.data?.object?.status || '',
            total: event?.data?.object?.total || 0,
            amount_currency: event?.data?.object?.currency || '',
        }

        await dbService.createDocument(Invoice, data);
        
        return true;
    } catch (error) {
        handleError(error, 'Error - createInvoiceFromEvent');
        return false;
    }
}

const getInvoice = async (req) => {
    try {
        return dbService.getAllDocuments(Invoice, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error in admin  getall invoice service');
    }
}

module.exports = {
    getInvoice,
    createInvoiceFromEvent
}