from src.chatflow_langchain.service.gemini.title.config import QUOTES, DEFAULT_TITLES
import random
import re
from src.logger.default_logger import logger

def extract_google_genai_error_message(error_message):
    try:
        # Isolate the part after the square bracket containing 'message'
        message_part = error_message.split('message: "', 1)[1]
        # Extract the message before the next double quote
        error_content = message_part.split('"')[0]
        return error_content
    except Exception as e:
        logger.error(f"Failed to extract google GenAI error message: {e}")
        return "An unknown error occurred"

def extract_google_error_message(error_message):
    try:
        # Regex to extract the exception name (e.g., 'NotFound')
        # exception_match = re.search(r"exceptions\.(\w+)", error_message)
        # exception_name = exception_match.group(1) if exception_match else "UnknownException"
        
        # Regex to extract the message inside the parentheses
        message_match = re.search(r"\('([^']+?)(?:\. |$)", error_message)
        
        if message_match:
            extracted_message = message_match.group(1)
        else:
            extracted_message = "An unknown error message"
        
        return extracted_message
    except Exception as e:
        logger.error(f"Failed to extract GenAI error message: {e}")
        return "An unknown error occurred", None
    
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