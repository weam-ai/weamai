const morgan = require('morgan');

const morganLogger = morgan('dev', {
    stream: {
        write: (str) => {
            logger.info(str);
        }
    }
})

module.exports = morganLogger;