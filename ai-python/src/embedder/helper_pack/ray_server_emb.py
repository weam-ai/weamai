import requests
import json
from src.logger.default_logger import logger
def send_post_request(url, texts_chunks_docs):
    headers = {'Content-Type': 'application/json'}
    data = {
        "input": texts_chunks_docs
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad requests (4XX or 5XX)
        return json.loads(response.text)
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error occurred: {err}", exc_info=True)
    except requests.exceptions.RequestException as err:
        logger.error(f"Request error occurred: {err}", exc_info=True)
    except Exception as err:
        logger.error(f"Unexpected error occurred: {err}", exc_info=True)

