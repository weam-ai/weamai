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