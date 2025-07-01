import ast
from src.logger.default_logger import logger
import asyncio
import base64
from pathlib import Path
from mimetypes import guess_type
import requests

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
    

async def get_next_token_within(stream_iter, timeout=1.0):
    try:
        return await asyncio.wait_for(stream_iter.__anext__(), timeout)
    except (StopAsyncIteration, asyncio.TimeoutError):
        return None
    



async def encode_image_to_base64(image_path_or_url: str) -> str:
    if image_path_or_url.startswith("http://") or image_path_or_url.startswith("https://"):
        response = requests.get(image_path_or_url)
        content_type = response.headers.get('Content-Type')
        if not content_type or not content_type.startswith("image/"):
            raise ValueError("URL does not point to a valid image.")
        encoded_string = base64.b64encode(response.content).decode("utf-8")
        return f"data:{content_type};base64,{encoded_string}"
    else:
        mime_type, _ = guess_type(image_path_or_url)
        if not mime_type:
            raise ValueError("Unsupported image format or unknown MIME type.")
        with open(image_path_or_url, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:{mime_type};base64,{encoded_string}"