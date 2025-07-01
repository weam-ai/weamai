import ast
from src.logger.default_logger import logger
from src.chatflow_langchain.service.openai.title.config import QUOTES, DEFAULT_TITLES
import random
import re

def extract_error_message(error_message):
    try:
        # Split the error message to isolate the dictionary part
        dict_str = error_message.split(' - ', 1)[1]
        
        # Convert the string to a dictionary
        error_dict = ast.literal_eval(dict_str)
        
        # Extract the desired message
        error_content = error_dict['error']['message']
        error_code = error_dict['error']['code']
        return error_content,error_code
    
    except Exception as e:
        # Handle exceptions that may occur during extraction
        logger.error(f"Failed to extract error message: {e}")
        return "An unknown error occurred"
    
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