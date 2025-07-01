import ast
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