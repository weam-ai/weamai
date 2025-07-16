const winston = require('winston');
require('winston-daily-rotate-file');
const config = require('../config/config');
const { format, transports } = winston;
const fs = require('fs');
const path = require('path');



// ✅ Create log folders if they don't exist
const logDirs = [
  path.join(__dirname, '..', 'storage', 'info'),
  path.join(__dirname, '..', 'storage', 'error'),
];

logDirs.forEach((dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`📁 Created log directory: ${dirPath}`);
  }
});
console.log("🚀 ~  config.SERVER.LOCAL_LOG:",  config.SERVER.LOCAL_LOG)

// Custom format to handle errors and stack traces
const errorStackFormat = format((info) => {
  if (info instanceof Error) {
    return {
      ...info,
      message: info.message,
      stack: info.stack
    };
  }
  
  if (info.error && info.error instanceof Error) {
    return {
      ...info,
      message: info.message || info.error.message,
      stack: info.error.stack
    };
  }
  
  return info;
});

const consoleFormat = format.combine(
  errorStackFormat(),
  format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  config.SERVER.LOCAL_LOG ? format.colorize() : format.uncolorize(),
  format.printf(({ timestamp, level, message, stack, ...metadata }) => {
    const status = metadata?.status ? ` [STATUS: ${metadata.status}]` : '';
    const stackTrace = stack ? `\n${stack}` : '';
    return `${timestamp} ${level}: ${message}${status}${stackTrace}`;
  })
);

const logger = winston.createLogger({
  level: 'debug',
  transports: [
    new transports.Console({
      format: consoleFormat,
    }),
  ],
});

module.exports = logger;
