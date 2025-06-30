from src.prompts.langchain.openai.additional_info_prompt import prompt_mapper
from src.logger.default_logger import logger
from src.celery_worker_hub.web_scraper.utils.hash_function import hash_website

def format_list_pairs_handler(list1, list2):
    """
    Pair elements from two lists and return a formatted string.
    
    Args:
    - list1 (list): First list containing the keys.
    - list2 (list): Second list containing either summaries or dictionary values.
      
    Returns:
    - str: Formatted string based on the structure of list2.
    """
    if not list1 or not list2:
        logger.info("One or both lists are empty. Returning empty string.")
        return ''
    
    # Check the structure of list2
    if isinstance(list2, dict):
        # If list2 contains dictionaries, use the hash-based format
        result = '; '.join(
            f"{list1[i]}:Summary {list2[hash_website(list1[i])]['summary']}" for i in range(len(list1))
        )
    else:
        # If list2 contains simple values, use the simple pairing format
        result = '; '.join(
            f"{list1[i]}:Summary {list2[i]}" for i in range(min(len(list1), len(list2)))
        )
    
    logger.debug(f"Formatted list pairs: {result}")
    return result

def fill_template(template_key, values):    
    template = prompt_mapper.get(template_key)
    if template:
        keys = [key for key in template.split('{')[1:] if '}' in key]
        logger.info(f"Keys found in template: {keys}")
        for key in keys:
            key = key.split('}')[0]
            if key not in values:
                values[key] = ' '
                logger.info(f"Added missing key '{key}' with default value ' '")

        try:
            return template.format(**values)
        except KeyError as e:
            logger.error(f"Missing value for placeholder: {e}", exc_info=True, extra={
                "tags": {"method": "ToolStreamingService.fill_template"}
            })
            return f"Missing value for placeholder: {e}"
    else:
        logger.warning(f"Template with key '{template_key}' not found.", extra={
            "tags": {"method": "ToolStreamingService.fill_template"}
        })
        return "Template not found"
    
def format_website_summary_pairs(websites, summaries):
    """
    Formats the pairs of websites and summaries.
    
    Args:
        websites (list): List of website URLs.
        summaries (list): List of corresponding summaries.
    
    Returns:
        list: A list of formatted pairs of websites and summaries.
    """
    formatted_pairs = format_list_pairs_handler(websites, summaries)
    return formatted_pairs if formatted_pairs else ''