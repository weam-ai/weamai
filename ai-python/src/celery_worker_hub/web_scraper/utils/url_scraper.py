import requests
from bs4 import BeautifulSoup
from src.logger.default_logger import logger
from src.celery_worker_hub.web_scraper.utils.prompt_notification import add_notification_data
from src.Firebase.firebase import firebase
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG
from requests.exceptions import RequestException
from urllib.parse import urlparse

def clean_list(items):
    seen = set()
    clean_items = []
    for item in items:
        item = item.strip()
        if item and item not in seen:
            clean_items.append(item)
            seen.add(item)
    clean_items = " ".join(clean_items)
    return clean_items

def is_valid_url(url: str) -> bool:
    """
    Check if the URL is well-formed and reachable.
    """
    try:
        # Check if the URL is properly formatted
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return False

        # Define a headers dictionary to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        # Consider the URL valid if the response status is 200-399
        return 200 <= response.status_code < 400
    except RequestException as e:
        logger.error(f"Request failed for URL: {url}, Error: {e}")
        return False

def get_user_agents():
    """Function to return a list of user-agent strings and additional headers."""
    return [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4.1 Safari/605.1.15',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/89.0',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Linux; U; Android 4.0; en-US; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        },
        {
            'User-Agent': 'Opera/9.80 (Windows NT 6.0; U; en) Presto/2.12.388 Version/12.18',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Accept': 'text/html, application/xml;q=0.9, */*;q=0.8',
        },
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
    ]

def web_scraping(url,notification_data):
    try:
        user_agents = get_user_agents()
        for headers in user_agents:
            html_content = requests.get(url, headers=headers, timeout=30)
            if html_content.status_code == 200:
                soup = BeautifulSoup(html_content.text, 'html.parser')
                logger.info(f"Successfully fetched URL: {url} with User-Agent: {headers['User-Agent']}")
                # return soup
                break
            logger.error(f"Received status code {html_content.status_code} for User-Agent: {headers['User-Agent']}")
        if html_content.status_code != 200:
            html_content.raise_for_status()

    except requests.exceptions.RequestException as e:
        try:
            if html_content.status_code == 403:
                forbidden_message = DEV_MESSAGES_CONFIG.get("url_forbidden_message")
                full_message = f"{forbidden_message}: {url}"
                firebase.send_push_notification(notification_data['token'],f"🚫 Access Denied: Scraping Blocked for URL Access", full_message)
                add_notification_data(full_message,notification_data["user_data"],"notificationList")
                logger.warning("🚫 403 Forbidden: Access to the URL %s is forbidden.", url)
                return '403'
            else:
                logger.error("Error fetching the URL %s: %s", url, e)
                return ' '
        except Exception as e:
            logger.error("Error parsing the HTML content for URL %s: %s", url, e)
            return ' '
    except Exception as e:
        logger.error("Error parsing the HTML content for URL %s: %s", url, e)
        return ' '

    try:
        lang = soup.html.get('lang')
   
    except Exception as e:
        logger.error("Error extracting language for URL %s: %s", url, e)
        lang = None

    try:
        title = soup.title.string
    except Exception as e:
        logger.error("Error extracting title for URL %s: %s", url, e)
        title = None

    try:
        meta = [f"{meta.get('name')}: {meta.get('content')}" for meta in soup.find_all('meta') if meta.get('name')]
 
    except Exception as e:
        logger.error("Error extracting meta tags for URL %s: %s", url, e)
        meta = []

    try:
        img_tags = soup.find_all('img')
        image_list = []
        for img in img_tags:
            alt_text = img.get('alt', '')
            image_list.append(alt_text)
    except:
        logger.error("Error extracting image information for URL %s: %s", url, e)
        image_list = []

    try:
        contacts = soup.find_all(['address', 'a'], text=lambda t: t and ('contact' in t.lower() or 'email' in t.lower() or 'phone' in t.lower()))
        contact_texts = [contact.get_text() for contact in contacts]
  
    except Exception as e:
        logger.error("Error extracting contact information for URL %s: %s", url, e)
        contact_texts = []

    try:
        social_links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(platform in href for platform in ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']):
                social_links.append(href)
  
    except Exception as e:
        logger.error("Error extracting social media links for URL %s: %s", url, e)
        social_links = []

    try:
        nav_items = [nav.get_text() for nav in soup.find_all('nav')]
  
    except Exception as e:
        logger.error("Error extracting navigation items for URL %s: %s", url, e)
        nav_items = []

    try:
        products = [prod.get_text() for prod in soup.find_all(['div', 'section'], class_=lambda x: x and 'product' in x.lower())]
  
    except Exception as e:
        logger.error("Error extracting product information for URL %s: %s", url, e)
        products = []

    try:
        headings = [heading.get_text() for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    except Exception as e:
        logger.error("Error extracting headings for URL %s: %s", url, e)
        headings = []

    try:
        footer = soup.body.find('footer')
        if footer:
            footer.extract()
        texts = [text.get_text() for text in soup.find_all('p')]
        filtered_texts = [text for text in texts if text.strip()]
      
    except Exception as e:
        logger.error("Error extracting texts for URL %s: %s", url, e)
        filtered_texts = []

    # Footer
    try:
        footer_texts = []
        if footer:
            footer_texts = [text.get_text() for text in footer.find_all('p')]

    except Exception as e:
        logger.error("Error extracting footer texts for URL %s: %s", url, e)
        footer_texts = []

    try:
        list_tags = soup.find_all(['ul', 'ol'])
        list_items = []
        for list_tag in list_tags:
            items = [li.get_text() for li in list_tag.find_all('li')]
            list_items.extend(items)
       
    except Exception as e:
        logger.error("Error extracting list items for URL %s: %s", url, e)
        list_items = []

    page_analysis = {
        'language': lang,
        'title': title,
        'meta_tags': meta,
        'images':image_list,
        'contact_info': contact_texts,
        'social_links': social_links,
        'navigation': nav_items,
        'product_info': products,
        'headings': headings,
        'texts': filtered_texts,
        'footer': footer_texts,
        'lists': list_items
    }
    try:
        page_analysis['contact_info'] = clean_list(page_analysis['contact_info'])
        page_analysis['social_links'] = clean_list(page_analysis['social_links'])
        page_analysis['navigation'] = clean_list(page_analysis['navigation'])
        page_analysis['product_info'] = clean_list(page_analysis['product_info'])
        page_analysis['headings'] = clean_list(page_analysis['headings'])
        page_analysis['texts'] = clean_list(page_analysis['texts'])
        page_analysis['footer'] = clean_list(page_analysis['footer'])
        page_analysis['lists'] = clean_list(page_analysis['lists'])
        page_analysis['meta_tags'] = clean_list(page_analysis['meta_tags'])
        page_analysis['images'] = clean_list(page_analysis['images'])
        page_analysis = " ".join(f'{page}:{page_analysis[page]}' for page in page_analysis)
    except Exception as e:
        logger.error("Error cleaning or joining analysis data for URL %s: %s", url, e)
        return page_analysis

    return page_analysis
