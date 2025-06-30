const EmailTemplate = require('../models/emailTemplate');
const { EMAIL_TEMPLATE } = require('../config/constants/common');

/**
 * Converts an HTML template string by replacing placeholders with actual data.
 * @param {string} htmlString - The HTML template string containing placeholders.
 * @param {Object} payload - An object containing data to replace placeholders in the template.
 * @returns {string} - The modified HTML template string with replaced placeholders.
 *                    Returns an empty string if the payload is empty.
 * @throws {Error} - Throws an error if there is an issue during the conversion process.
 */
const convertTemplateToString = (htmlString, payload) => {
    try {
        // Make a copy of the original HTML string.
        let str = htmlString;

        // Iterate through the payload and replace placeholders in the HTML string.
        for (const key in payload) {
            if (!payload.hasOwnProperty(key)) {
                continue;
            }
            const matchedKey = `{{${key}}}`;
            str = str.replaceAll(matchedKey, payload[key]);
        }

        // If payload is not empty, return the modified HTML string; otherwise, return an empty string.
        if (Object.keys(payload).length) return str;
        else return '';
    } catch (error) {
        handleError(error, 'Error in convertTemplateToString');
    }
};

/**
 * Retrieves the header content from an array of email template contents.
 * @param {Array} contents - Array of email template contents.
 * @returns {Object|null} - The header content object if found, otherwise null.
 */
const getHeaderContent = (contents) => {
    // Find and return the content with the specified code for the header.
    return contents.find((content) => content.code === EMAIL_TEMPLATE.HEADER_CONTENT);
};

/**
 * Retrieves the footer content from an array of email template contents.
 * @param {Array} contents - Array of email template contents.
 * @returns {Object|null} - The footer content object if found, otherwise null.
 */
const getFooterContent = (contents) => {
    // Find and return the content with the specified code for the footer.
    return contents.find((content) => content.code === EMAIL_TEMPLATE.FOOTER_CONTENT);
};

/**
 * Asynchronous function to retrieve an email template based on a given code and compact data.
 * @param {string} code - The code of the email template to retrieve.
 * @param {object} compactData - Data to be used for replacing placeholders in the template.
 * @returns {Promise<object>} - A promise that resolves to the final email template.
 */
const getTemplate = async (code, compactData) => {
    // Fetch the main email template by code, retrieving only necessary fields (body, subject, code).
    const template = await EmailTemplate.findOne({ code: code }, { body: 1, subject: 1, code: 1 }).lean();

    // Fetch additional contents (header and footer) based on predefined template codes.
    const contents = await EmailTemplate.find({
        code: {
            $in: [
                EMAIL_TEMPLATE.HEADER_CONTENT,
                EMAIL_TEMPLATE.FOOTER_CONTENT,
            ],
        },
    }, { body: 1, subject: 1, code: 1 }).lean();

    // Extract header content from the fetched contents.
    const header = getHeaderContent(contents);

    // Extract footer content from the fetched contents.
    const footer = getFooterContent(contents);

    // Set the header and footer content in the main template body.
    const body = setHeaderAndFooter(template.body, {
        header: header.body,
        footer: footer.body,
    });

    // Convert the template body to a string, replacing placeholders with actual data.
    template.body = convertTemplateToString(body, compactData);

    // Return the final email template.
    return template;
};

/**
 * Sets the header and footer content in the provided email template body.
 * @param {string} body - The email template body where placeholders will be replaced.
 * @param {Object} obj - An object containing header and footer content.
 * @param {string} obj.header - The header content to replace the '{{header}}' placeholder.
 * @param {string} obj.footer - The footer content to replace the '{{footer}}' placeholder.
 * @returns {string} - The modified email template body with header and footer content.
 */
const setHeaderAndFooter = (body, obj) => {
    // Replace the '{{header}}' and '{{footer}}' placeholders in the body with actual content.
    return body
        .replace('{{header}}', obj.header)
        .replace('{{footer}}', obj.footer);
};


module.exports = {
    getTemplate
}