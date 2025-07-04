import re
import ast
from typing import Tuple
from src.logger.default_logger import logger
from fastapi import status
import json
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.crypto_hub.utils.crypto_utils import crypto_service
from src.db.config import get_field_by_name
from threading import Thread, Lock
import os
import time
import aiohttp
import asyncio

thread_repo = ThreadRepostiory()

async def replace_citations(text, urls, full_message):
    def replacement(match):
        try:
            indices = match.group(0)[1:-1].split('][')
            formatted_links = ', '.join(f'[{i}]({urls[int(i) - 1]})' for i in indices if int(i) - 1 < len(urls))
            return formatted_links
        except (IndexError, ValueError, AttributeError):
            return match.group(0)

    # Regex pattern to find citations like [3][4], [3], etc.
    citation_pattern = r'\[(\d+)\](?:\[(\d+)\])*(?=[.\n]|$)'

    # Regex pattern to match code blocks
    code_block_pattern = r'```'
    full_message += text
    # Check if there is any citation pattern in the full_message
    has_citations = re.search(citation_pattern, full_message)

    # Check if all code blocks are properly closed
    unclosed_code_blocks = len(re.findall(code_block_pattern, full_message)) % 2 != 0

    if has_citations and not unclosed_code_blocks:
        # Split the text into code and non-code sections
        sections = re.split(f'({code_block_pattern}.*?{code_block_pattern})', text, flags=re.S)

        # Process only non-code sections
        for i in range(len(sections)):
            # Check if the section is not a code block
            if not (sections[i].startswith('```') and sections[i].endswith('```')):
                sections[i] = re.sub(citation_pattern, replacement, sections[i])

        # Combine the sections back into a single string
        return ''.join(sections)

    # If no citation pattern is found or there are unclosed code blocks, return the text unchanged
    return text

def extract_perplexity_error_message(error_message: str) -> Tuple[str, str]:
    """
    Extracts the error content and error code from an error message string.
    
    Parameters:
    - error_message (str): The raw error message string.
    
    Returns:
    - Tuple[str, str]: Extracted error content and error code.
    """
    try:
        # Split the error message to isolate the dictionary part
        if ' - ' in error_message:
            dict_str = error_message.split(' - ', 1)[1]
        else:
            logger.warning("Unexpected error message format")
            return "We're experiencing a temporary issue. Please retry in a few moments.", "common_response"
        
        # Convert the string to a dictionary
        error_dict = ast.literal_eval(dict_str)
        
        # Extract the desired message and code, ensuring both keys exist
        error_content = error_dict.get('error', {}).get('message', "No message provided")
        error_code = error_dict.get('error', {}).get('code', "common_response")
        
        return error_content, error_code
    
    except Exception as e:
        logger.error(f"Failed to extract error message: {e}")
        return "We're experiencing a temporary issue. Please retry in a few moments.", "common_response"

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
        logger.error(f"Failed to extract error message: {e}")
        return "We're experiencing a temporary issue. Please retry in a few moments.", "common_response"
    
def chat_perplexity_exception_handler(exception, thread_id, collection_name):
    try:
        error_content, error_code = extract_perplexity_error_message(str(exception))

        # Log error details
        if error_code not in OPENAI_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.ChatPerplexityException"}}
            )
        else:
            logger.error(
                f"🚨 ChatPerplexity Exception occurred: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.ChatPerplexityException"}}
            )

        # Update thread repository
        thread_repo.initialization(thread_id, collection_name)
        thread_repo.add_message_openai(error_code)

        # Respond with a user-friendly message
        content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
        return json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

    except Exception as inner_exception:
        # Handle any errors during exception handling
        logger.error(
            f"🚨 Failed to handle ChatPerplexityException: {inner_exception}",
            extra={"tags": {"method": "PerplexityChatService.stream_run_conversation.ChatPerplexityException"}}
        )
        thread_repo.initialization(thread_id, collection_name)
        thread_repo.add_message_openai("common_response")
        content = OPENAI_MESSAGES_CONFIG.get("common_response")
        return json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class PERPLEXITYAPIKeyManager(metaclass=Singleton):
    def __init__(self, api_key_details=None, reset_interval=60):
        """
        Initialize the PERPLEXITYAPIKeyManager.

        :param api_key_details: Dictionary of API keys with their names as keys and keys as values.
        :param reset_interval: Time interval in seconds to reset key usage (default is 60 seconds).
        """
        self.api_keys = api_key_details
        self.api_key_list = list(api_key_details.keys()) if api_key_details else []
        self.key_usage = {key: 0 for key in self.api_keys.keys()} if api_key_details else {}
        self.current_index = 0
        self.lock = Lock()
        self.reset_interval = reset_interval  # Reset every 1 minute

        # Start the reset timer in a separate thread
        self.reset_thread = Thread(target=self._reset_key_usage, daemon=True)
        self.reset_thread.start()

    def get_api_key(self):
        """
        Get the next API key, rotating among the available keys, and increment its usage count.

        :return: The current API key value.
        """
        with self.lock:
            # Get the current key
            api_key_name = self.api_key_list[self.current_index]
            self.key_usage[api_key_name] += 1

            self.current_index = (self.current_index + 1) % len(self.api_key_list)

            perplexity_key = self.api_keys[api_key_name]
            return decryptor.decrypt(perplexity_key)

    def _reset_key_usage(self):
        """
        Reset the usage count of all keys at regular intervals, starting from the first key.
        """
        while True:
            time.sleep(self.reset_interval)
            with self.lock:
                # Reset usage counts and reset index to 0
                self.key_usage = {key: 0 for key in self.api_keys.keys()}
                self.current_index = 0  # Reset index to start from key1
                # logger.info("PERPLEXITY APIKey usage has been reset.")
            
perplexity_api_keys = get_field_by_name('setting', 'PERPLEXITY_APIKEY', 'details')
perplexity_manager = PERPLEXITYAPIKeyManager(perplexity_api_keys, reset_interval=60)  # Reset every 1 minute÷

async def fetch_status(session, url):
    """Fetch the HTTP status code for a given URL."""
    try:
        async with session.head(url, timeout=5) as response:
            content_type = response.headers.get("Content-Type", "")
            return response.status,content_type, url
    except Exception:
        return None, url

async def filter_valid_images(image_data):
    """Filter valid image URLs with a 200 status code."""
    valid_images = []
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, image['image_url']) for image in image_data]
        results = await asyncio.gather(*tasks)

        for result, image in zip(results, image_data):
            if result[0] == 200 and result[1].startswith("image"):  # If the status code is 200
                valid_images.append(image)
    return valid_images