import os
import re
from urllib.parse import urlparse

def is_probable_blog_url(url):
    """
    Applies heuristics to determine if a URL is likely a blog or article page.
    """
    # Exclude URLs that point to known file extensions (fallback list)
    excluded_extensions = {'.pdf', '.doc', '.docx', '.png', '.jpg', '.jpeg', 
                           '.gif', '.zip', '.xls', '.xlsx', '.ppt', '.pptx', 
                           '.csv', '.txt', '.mp3', '.mp4', '.avi', '.mkv', 
                           '.wav', '.flac', '.mov', '.exe', '.bin', '.iso', 
                           '.tar', '.gz', '.7z', '.rar', '.svg', '.webp', '.json'
                           '.bmp', '.tiff', '.ico', '.epub', '.mobi', '.apk', 
                           '.dmg', '.pkg', '.deb', '.rpm', '.log', '.bak', 
                           '.tmp', '.swf', '.psd', '.ai', '.indd', '.dwg', 
                           '.cad', '.torrent', '.vob', '.srt', '.ass', '.sub'}
    
    path = urlparse(url).path
    ext = os.path.splitext(path)[1].lower()

    # Rule 1: Must not be a file download based on extension
    if ext in excluded_extensions:
        return False

    return True

def generate_seo_friendly_url(website_url, primary_keywords):
    if not primary_keywords:
        return None
    
    # Generate the formatted keyword by converting to lowercase and replacing spaces with hyphens
    formatted_keyword = primary_keywords[0].lower().replace(" ", "-")
    
    # Clean up the formatted keyword by stripping spaces
    formatted_keyword = formatted_keyword.strip()
    
    # Create SEO-friendly URL
    cleaned_website_url = website_url.rstrip("/")
    seo_friendly_url = f"{cleaned_website_url}/{formatted_keyword}" if formatted_keyword else None
    
    return seo_friendly_url

# def sort_keywords_by_competition(data):
#     # Get the list of keywords
#     if isinstance(data, dict):
#         keywords = data.get('data', {}).get('recommended_keywords', [])
#     elif isinstance(data, list):
#         keywords = data
#     else:
#         keywords = []

#     # Sorting order: High < Medium < Low
#     competition_order = {'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}

#     # Sort by competition
#     return sorted(keywords, key=lambda x: competition_order.get(x.get('competition'), 3))

def sort_keywords_by_competition(data):
    if isinstance(data, dict):
        keywords = data.get('data', {}).get('recommended_keywords', [])
    elif isinstance(data, list):
        keywords = data
    else:
        keywords = []

    # Define sorting priority for competition
    competition_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}

    # Sort by competition (HIGH first), then by search volume (descending)
    return sorted(
        keywords,
        key=lambda x: (
            competition_order.get(str(x.get('competition', '')).upper(), 3),
            -x.get('search_volume', 0)
        )
    )

def refined_keyword_data(items, prefix):
    return [
        {
            "id": f"{prefix}-{index}",
            "keyword": item.get("keyword", "None"),
            "search_volume": item.get("search_volume") or 0,
            "competition": (item.get("competition") or "LOW").capitalize()
        }
        for index,item in enumerate(items)
        if isinstance(item, dict)
    ]