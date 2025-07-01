import ast
from src.logger.default_logger import logger

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