const { JOB_TYPE } = require('../config/constants/common');
const { AWS_CONFIG, EMAIL } = require('../config/config');
const AWS = require('aws-sdk');
const nodemailer = require('nodemailer');
const Util = require('util');
const { createJob } = require('../jobs');
const EmailTemplate = require('../models/emailTemplate');
const dbService = require('../utils/dbService');
const path = require('path');
const fs=require('fs');
const { ENV_VAR_VALUE } = require('../config/constants/common');

const sendEmail = async (obj) => {
    try {
        let transporter;
        
        if(EMAIL.EMAIL_PROVIDER === ENV_VAR_VALUE.SES){
            AWS.config.update({
                apiVersion: AWS_CONFIG.AWS_S3_API_VERSION,
                region: AWS_CONFIG.REGION
            })

            transporter = nodemailer.createTransport({ SES: new AWS.SES({}) });
        } else {
            transporter = nodemailer.createTransport({
                host: EMAIL?.SMTP_SERVER,
                port: EMAIL?.SMTP_PORT, // Gmail SMTP requires port 587, not 25
                secure: EMAIL?.SECURE === 'true', // Use STARTTLS for port 587
                auth: {
                    user: EMAIL?.SMTP_USER,
                    pass: EMAIL?.SMTP_PASSWORD
                },
                tls: {
                    rejectUnauthorized: false // Handle self-signed certificates
                }
            });    
        }
       
        const mailOptions = {
            from: EMAIL?.SENDER_EMAIL,
            to: obj.email,
            subject: obj.subject,
            html: obj.htmlData,
            attachments: obj.attachments || [],
            cc: obj.ccEmails,
            bcc: obj.bccEmails,
        };
        const sendMail = Util.promisify(transporter.sendMail.bind(transporter));
        const response = await sendMail(mailOptions);
        logger.info(`Mail response: ${response.response} - ${response.envelope.to}`);
    } catch (error) {
        logger.error('Error in sendEmail', error);
    }
}

const sendSESMail = async (email, subjectData, htmlContentData, attachments = [], ccEmails, bccEmails,) => {
    try {
        const imagePath = path.join(__dirname, '../../public/images/weam-logo.png');
        
        // Check if file exists
        if (!fs.existsSync(imagePath)) {
            console.error('Image not found at:', imagePath);
            throw new Error('Logo image not found');
        }
        const imageBuffer = fs.readFileSync(imagePath);
        const base64Image = imageBuffer.toString('base64');
        
        
        // Create the inline image attachment
        const inlineImage = {
            filename: 'weam-logo.png',
            content: base64Image,
            cid: 'logoImageCid',
            contentType: 'image/png',
            contentDisposition: 'inline',
            encoding: 'base64'
        };
        
        
        attachments.push(inlineImage);
        
        const mailObj = {
            email: email,
            subject: subjectData,
            htmlData: htmlContentData,
            attachments: attachments,
            ccEmails,
            bccEmails,
        }
        await createJob(JOB_TYPE.SEND_MAIL, mailObj)
    } catch (error) {
        handleError(error, 'Error in sendSESMail');
    }
}

async function updateEmailTemplate(req) {
    try {
        return EmailTemplate.findOneAndUpdate({ code: req.body.code }, req.body, { new: true, upsert: true });
    } catch (error) {
        handleError(error, 'Error - updateEmailTemplate');
    }
}

async function viewEmailTemplate(req) {
    try {
        return EmailTemplate.findById({ _id: req.params.id });
    } catch (error) {
        handleError(error, 'Error - viewEmailTemplate');
    }
}

async function deleteEmailTemplate(req) {
    try {
        return EmailTemplate.deleteOne({ _id: req.params.id });
    } catch (error) {
        handleError(error, 'Error - deleteEmailTemplate');
    }
}

async function listEmailTemplate(req) {
    try {
        return dbService.getAllDocuments(EmailTemplate, req.body.query || {}, req.body.options || {});
    } catch (error) {
        handleError(error, 'Error - listEmailTemplate');
    }
}

module.exports = {
    sendEmail,
    sendSESMail,
    updateEmailTemplate,
    viewEmailTemplate,
    deleteEmailTemplate,
    listEmailTemplate
}