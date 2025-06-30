import ast
from io import BytesIO
from PIL import Image
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

def convert_image_to_bytes(image: Image.Image) -> bytes:
    """
    Convert a PIL Image to bytes.
    """
    # Create an in-memory byte stream
    buffer = BytesIO()
    # Save the image in its original format to the byte stream
    image_format = image.format or "PNG"  # Fallback to PNG if format is None
    image.save(buffer, format=image_format)
    buffer.seek(0)  # Ensure the stream is at the beginning
    return buffer.getvalue()


def delete_resources(response=None, image_bytes=None, client=None):
    for var in [response, image_bytes, client]:
        if var is not None:
            del var