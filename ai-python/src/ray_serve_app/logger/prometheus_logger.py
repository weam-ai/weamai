import os
import logging
import logging_loki
from dotenv import load_dotenv

load_dotenv()
LOKI_LOGGING_URL = os.environ.get("LOKI_LOGGING_URL", "http://loki:3100/loki/api/v1/push")


# Configure the LokiHandler
handler = logging_loki.LokiHandler(
    url=LOKI_LOGGING_URL,
    tags={"application": "gocustom"},
    version="1",
)

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
