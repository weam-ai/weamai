/*
 * Database connection file.
 */
const mongoose = require('mongoose');
const { MONGODB } = require('./config');
const logger = require('../utils/logger');
// const dbConfigure = `${MONGODB.DB_USERNAME}${MONGODB.DB_PASSWORD}`;
// const dbConnection = `${MONGODB.DB_CONNECTION}://${dbConfigure}${MONGODB.DB_HOST}${MONGODB.DB_PORT}/${MONGODB.DB_DATABASE}?retryWrites=true&w=majority&readPreference=nearest`;
const dbConnection = MONGODB.DB_URI;

mongoose.connect(dbConnection);
// TODO: Remove debug in production

mongoose.set('debug', false);
const db = mongoose.connection;

db.once('open', () => {
    logger.info('MongoDB Connection Succeed');
});

db.on('error', () => {
    logger.info('Error in Connect Mongo');
});

module.exports = mongoose;