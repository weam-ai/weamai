const moment = require('moment-timezone');
const { TZ } = require('../config/config');

const DATE_FORMAT = 'YYYY-MM-DD HH:mm:ss';

const convertToTz = function (params) {
    try {
        const obj = { ...params };
        const defaultTimezone = TZ;
        const requestTimezone = obj?.tz ? obj.tz : defaultTimezone;
        if (obj && obj.date === undefined) {
            obj.date = moment()
                .tz(requestTimezone)
                .format(DATE_FORMAT);
        }
        const format = obj?.format ? obj.format : DATE_FORMAT;
        let convertedDateTime = moment(obj.date);
        if (requestTimezone !== defaultTimezone) {
            convertedDateTime = moment(obj.date).tz(requestTimezone);
        }
        let serverTimeZone = moment(obj.date, defaultTimezone);
        let localOffset = serverTimeZone.utcOffset();
        serverTimeZone.tz(requestTimezone);
        let centralOffset = serverTimeZone.utcOffset();
        let diffInMinutes = localOffset - centralOffset;
        const date = convertedDateTime.tz(defaultTimezone);

        return date.add(diffInMinutes, 'minutes').format(format);
    } catch (error) {
        handleError(error, 'Error - convertToTz');
    }
};

const convertToRetriveTz = (params) => {
    try {
        const obj = { ...params };
        const defaultTimezone = TZ;
        const requestTimezone = obj?.tz ? obj.tz : defaultTimezone;
        if (obj && obj.date === undefined) {
            obj.date = moment().toISOString();
        }
        let format = obj?.format ? obj.format : DATE_FORMAT;
        let convertedDateTime = moment(obj.date);
        if (requestTimezone !== defaultTimezone) {
            convertedDateTime = moment(obj.date).tz(defaultTimezone);
        }
        const date = convertedDateTime.tz(requestTimezone);
        return format ? date.format(format) : date;
    } catch (error) {
        handleError(error, 'Error - convertToRetriveTz');
    }
};

module.exports = {
    convertToTz,
    convertToRetriveTz
}
