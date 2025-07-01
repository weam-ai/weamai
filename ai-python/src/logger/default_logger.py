import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import sys

# Define a custom logging filter to add the 'tags' attribute
class ContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'tags'):
            record.tags = ''  # or set a default value
        return True
    
PYTEST_RUNNING = any('pytest' in arg for arg in sys.argv)

# Configure log directory based on whether pytest is running or not
if PYTEST_RUNNING:
    # log_dir = 'src/logs/pytest_logs'
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/test_api_logs'))
else:
    log_dir = 'src/logs'

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

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