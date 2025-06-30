from src.celery_worker_hub.web_scraper.utils.hash_function import hash_website
def map_new_websites(summary_dict, new_websites):
    """
    This function takes a dictionary of old websites with their indexes (summary_dict)
    and a list of new websites. It checks if each new website exists in the summary dictionary.
    If it exists, it returns the index; otherwise, it returns 'Not Found'.
    
    Args:
    - summary_dict (dict): A dictionary where keys are old websites and values are their indexes.
    - new_websites (list): A list of new websites to be checked.
    
    Returns:
    - result (dict): A dictionary where new websites are mapped to their existing index
                     in summary_dict or 'Not Found' if they do not exist.
    """
    if summary_dict is not None:    
        result = {}
        websites = []
        for website in new_websites:
            # Hash the website URL using SHA-256
            hash_output = hash_website(website)
            
            # Check if the hash exists in the summary_dict
            if hash_output in summary_dict:
                result[hash_output] = summary_dict[hash_output]
            else:
                # If not found, return the original website and 'Not Found' status
                result[hash_output] = {'website': website, 'status': 'Not Found'}
                websites.append(website)
        return websites,result
    else:
        return new_websites,None