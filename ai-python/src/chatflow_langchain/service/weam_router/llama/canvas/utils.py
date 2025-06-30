import ast
from src.logger.default_logger import logger
from src.chatflow_langchain.service.weam_router.llama.title.config import QUOTES
import re

def regex_replace(regex_pattern, replacement_string,selected_text):
    """
    Function to replace a substring in the original string based on the provided regular expression pattern.
    
    Strictly,This function is designed to be invoked only once per execution to ensure efficiency and clarity in its operation.
    The Parameters Names below should not be changed
    Parameters:
    - regex_pattern (str): The regex pattern that identifies the substring(s) to replace.
    - replacement_string (str): The string that will replace the matched substring(s).The Replacement String should be revised on the basis of selected_text
    - selected_text(str):This is String which is to be replaced By replacement_string.It's the Reference For Replacement String.
    Returns:
    - str: The updated string after replacements. Only the first occurrence of the pattern will be replaced.
    """


        # Replace only the first occurrence of the pattern
    updated_string = re.sub(regex_pattern, replacement_string, count=1)
    
    return updated_string

def regex_replace_v2(regex_pattern, replacement_string, original_string, multiple_replacement=False):
    """
    Function to replace substring in the original string based on the provided regular expression pattern.
    
    Parameters:
    - regex_pattern (str): The regex pattern that identifies the substring(s) to replace.
    - replacement_string (str): The string that will replace the matched substring(s).
    - original_string (str): The string in which the replacement will occur.
    - multiple_replacement (bool): If True, replaces all matches. If False, only the first match will be replaced.
    
    Returns:
    - str: The updated string after replacements.
    """
    if multiple_replacement:
        # Replace all occurrences of the pattern
        updated_string = re.sub(regex_pattern, replacement_string, original_string)
    else:
        # Replace only the first occurrence of the pattern
        updated_string = re.sub(regex_pattern, replacement_string, original_string, count=1)
    
    return updated_string

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
def replace_substring(original_string: str, start: int, end: int, replacement: str) -> str:
    # Ensure the start and end indices are valid
    if start < 0 or end >len(original_string) or start > end:
        raise ValueError("Invalid start or end index")
    
    replacement_string = original_string[:start] + replacement
    replacement_string = replacement_string + original_string[end:]
    # Replace the substring and return the new string
    return original_string[:start] + replacement + original_string[end+1:]


def extract_languages(markdown_text):
    """Extract programming languages from markdown code blocks."""
    # List to store detected languages
    detected_languages = []

    # Regex pattern to identify code blocks with an optional language identifier
    code_block_pattern = r'```(\w*)\n.*?```'

    # Find all matches for the pattern
    matches = re.findall(code_block_pattern, markdown_text, re.DOTALL)

    # Append each found language to the list
    for match in matches:
        detected_languages.append(match if match else 'text')

    return detected_languages

def get_word_boundary_substring(text, start_index, end_index):
    """
    Given a content string and the indices of the user's selection, return
    the text surrounded by word boundaries, considering markdown formatting.
    """
    # Ensure indices are within bounds
    start_index = max(0, start_index)
    end_index = min(len(text), end_index)

    # Regular expression pattern to match words and markdown structures
    pattern = r'(\*\*.*?\*\*|\*.*?\*|`.*?`|!\[.*?\]\(.*?\)|\[.*?\]\(.*?\)|\S+)'
    end_pattern = r'[.!?;\n]'  # Pattern to match punctuation marks to end at

    # Search backwards for the start of the word/markdown structure
    adjusted_start = start_index
    for match in re.finditer(pattern, text):
        if match.start() <= start_index < match.end():
            adjusted_start = match.start()
            break

    # Search forwards for the end of the punctuation or end of markdown structure
    adjusted_end = end_index
    # Start by setting adjusted_end to end of the markdown structure if it is in the range
    for match in re.finditer(pattern, text):
        if match.start() <= end_index < match.end() or match.start() >= end_index:
            adjusted_end = match.end()
            break

    # Then extend adjusted_end to include punctuation if it exists
    punctuation_match = re.search(end_pattern, text[adjusted_end:])
    if punctuation_match:
        adjusted_end += punctuation_match.end()

    # Ensure we capture the correct selected text, including markdown if applicable
    selected_text = text[adjusted_start:adjusted_end]

    return selected_text, adjusted_start, adjusted_end