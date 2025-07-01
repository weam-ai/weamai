import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Define a custom logging filter to add the 'tags' attribute
class ContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'tags'):
            record.tags = ''  # or set a default value
        return True

# Specify the absolute path for the log directory
log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/test_logs'))

# Create the logs directory if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Get the current date for the log file name
current_date = datetime.now().strftime('%Y-%m-%d')
log_file = os.path.join(log_dir, f'log_{current_date}.log')

# Create a stream handler for logging to the console
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Create a formatter and add it to the stream handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(tags)s - %(message)s')
stream_handler.setFormatter(formatter)

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)

# Add the custom filter to the stream handler
stream_handler.addFilter(ContextFilter())

# Create a file handler for logging to a file
file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=10)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

logger.info("======================================= Starting Pytest Execution =======================================")
