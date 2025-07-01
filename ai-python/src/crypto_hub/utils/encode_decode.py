from src.logger.default_logger import logger
import base64
from typing import Optional

def encode_object(object_id: str) -> Optional[str]:
    """
    Encodes a hexadecimal string into a URL-safe Base64 string.
    
    :param object_id: Hexadecimal string to be encoded.
    :return: URL-safe Base64 encoded string or None if input is empty.
    """
    if not object_id:
        logger.warning("encode_object: function called with empty input.")
        return None
    
    try:
        buffer = bytes.fromhex(object_id)
        encoded = base64.urlsafe_b64encode(buffer).decode('utf-8')
        result = encoded.rstrip('=')
        logger.info("Successfully encoded object_id.")
        return result
    except ValueError:
        logger.error("encode_object: function Invalid hexadecimal input.")
        raise ValueError("Invalid hexadecimal input.")

def decode_object(encoded_id: str) -> Optional[str]:
    """
    Decodes a URL-safe Base64 string back to a hexadecimal string.
    
    :param encoded_id: URL-safe Base64 encoded string.
    :return: Decoded hexadecimal string or None if input is empty.
    """
    if not encoded_id:
        logger.warning("decode_object: function called with empty input.")
        return None
    
    try:
        base64_str = encoded_id + ('=' * (4 - len(encoded_id) % 4))  # Pad with '=' to make valid Base64
        buffer = base64.urlsafe_b64decode(base64_str)
        result = buffer.hex()
        logger.info("Successfully decoded encoded_id.")
        return result
    except (ValueError, base64.binascii.Error):
        logger.error("encode_object: function Invalid Base64 input.")
        raise ValueError("Invalid Base64 input.")