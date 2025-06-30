import re
import requests
import tldextract
from src.chatflow_langchain.service.pro_agent.video_analysis.config import VideoModel
def extract_video_id(url):
    # Extract video ID from Loom URL
    pattern = r'share/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Loom URL")

    
def get_video_url(video_id):
    # Get video details from Loom API
    api_url = f"https://www.loom.com/api/campaigns/sessions/{video_id}/transcoded-url"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Origin': 'https://www.loom.com',
        'Referer': f'https://www.loom.com/share/{video_id}',
        'Accept': 'application/json',
    }
    
    response = requests.post(api_url, headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch video details. Status code: {response.status_code}")
    
    data = response.json()
    try:
        video_url = data['url']
        print(f"Generated video URL: {video_url}")  # Debug print
        return video_url
        
    except KeyError as e:
        print(f"JSON Response: {data}")
        raise ValueError(f"Could not find video URL in response: {str(e)}")
    

def extract_main_domain(url: str) -> str:
    extracted = tldextract.extract(url)
    return extracted.domain

def get_cached_token_cost(token):
    return {"cache_total_cost": (token/1000000)*(VideoModel.ttls/60),"cache_prompt_tokens":token}