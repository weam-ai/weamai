import ast
from src.chatflow_langchain.service.multimodal_router.title.config import QUOTES, DEFAULT_TITLES
import random
import re
from src.logger.default_logger import logger

def extract_error_message(error_message):
    try:
        # Ensure the error message contains a structured error part
        if ' - ' not in error_message:
            raise ValueError("Unexpected error format")

        # Extract the dictionary part of the error message
        dict_str = error_message.split(' - ', 1)[1]
        
        # Convert the string to a dictionary using ast.literal_eval
        error_dict = ast.literal_eval(dict_str)

        # Extract required error details
        error_content = error_dict.get('error', {}).get('message', "Unknown error")
        error_code = error_dict.get('error', {}).get('code', "common_response")

        return error_content, error_code
    
    except Exception as e:
        logger.error(f"Failed to extract error message: {e}")
        return "An unknown error occurred", "common_response"
    
def remove_all_quotes(text):
    # List of all types of quotes to remove
    quotes = QUOTES.UNWANTED_QUOTES
    for quote in quotes:
        text = text.replace(quote, '')
    return text

def get_default_title(error_type=None):
    titles = DEFAULT_TITLES.TITLES.get(error_type, DEFAULT_TITLES.TITLES["default"])
    return random.choice(titles)

    
def remove_title_and_colon(input_string):
    # Strip leading/trailing spaces for consistency
    input_string = input_string.strip()
    
    # Use a regular expression to remove the first occurrence of "title" (case-insensitive) and ":" in order
    pattern = r'(?i)^title\s*:?\s*'  # Matches "title" at the start (case-insensitive), optional ":" and spaces
    result = re.sub(pattern, '', input_string, count=1)
    
    return result.strip()  # Remove any additional leading/trailing spaces