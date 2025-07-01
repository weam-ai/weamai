from botocore.exceptions import NoCredentialsError
from bson import ObjectId
from src.aws.boto3_client import Boto3S3Client
from src.aws.localstack_client import LocalStackS3Client
from src.aws.minio_client import MinioClient
import pandas as pd
from src.logger.default_logger import logger
from fastapi import HTTPException, status
import os
import io
import aiohttp
import asyncio
import tldextract
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import json
import socket
from src.crypto_hub.utils.crypto_utils import MessageDecryptor
from src.db.config import get_field_by_name
from threading import Thread, Lock
import time

ENCODING_NAME = "gpt2"  # or your actual encoding
TOKEN_LIMIT = 1_000_000  # 1,000,000 tokens max per file


from src.custom_lib.langchain.tiktoken_load.encoding_cache import get_cached_encoding
from src.aws.storageClient_service import ClientService
key = os.getenv("SECURITY_KEY").encode("utf-8")
decryptor = MessageDecryptor(key)


def attach_status_icon(status: str, message: str) -> str:
    """
    Attach an appropriate icon to a status message based on a dictionary mapping.
    
    :param status: Status key (e.g., "pass", "fail")
    :param message: The status message
    :return: The formatted status message with the correct icon
    """
    status_icons = {
        "pass": "✅",
        "fail": "❌",
      
    }
    
    icon = status_icons.get(status.lower(), "❓")
    return f"{icon} {message}"

def extract_json_block(text):
    match = re.search(r'```json\s*(\{.*?\}|\[.*?\])\s*```', text, re.DOTALL)
    if match:
        raw_json = match.group(1).strip()
        try:
            # First try direct loading (in case it's already valid JSON)
            return json.loads(raw_json)
        except json.JSONDecodeError:
            try:
                # Decode escaped characters and try again
                decoded = bytes(raw_json, "utf-8").decode("unicode_escape")
                return json.loads(decoded)
            except json.JSONDecodeError as e:
                print("JSON decoding failed:", e)
    return None


def attach_status_icon_list(results:dict,category_dict:dict) -> str:
    """
    Attach an appropriate icon to a status message based on a dictionary mapping.
    
    :param status: Status key (e.g., "pass", "fail")
    :param message: The status message
    :return: The formatted status message with the correct icon
    """
    status_icons = {
        "pass": "✅",
        "fail": "❌",
        '✓': "✅",
        '✗': "❌",
    }
    formatted_results = []
    if len(results) == 0:
        return ("", [], category_dict) 
    else:
        # IDs_list to replace the llm generated IDs with original One
        if not results or not results.get('checklist_item') or not results.get('text'):
            return ("", [], category_dict)

    # Handle the case where 'text' is a list instead of a dict
        text_data = results['text']
        if isinstance(text_data, list):
            # Assuming the structure is like [{'results': [...]}, ...]
            # Adjust according to your actual structure
            checklist_results = text_data
        elif isinstance(text_data, dict):
            checklist_results = text_data.get('results', [])
        else:
            return ("", [], category_dict)
        #IDs to category to maintain from where new category is to be shown in markdown
        id_to_category = {}
        for item in results['checklist_item']:
            for k, v in item.items():
                if k != 'category':
                    id_to_category[k] = item['category']
        # Format the results
        for result in checklist_results:
            status = result['status']
            message = result['note']
            icon = status_icons.get(status.lower(), "❓")
            result['status'] = icon
            if  category_dict[id_to_category[result['id']]]:
                formatted_results.append(f"\n\n{icon} {message}")
            else:
                formatted_results.append(f"\n\n### {id_to_category[result['id']]}\n\n{icon} {message}")
                category_dict[id_to_category[result['id']]] = True
        return ("".join(formatted_results),checklist_results,category_dict)
    


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

async def upload_df_to_s3(df,extract_data):
    """Uploads a file-like object to an S3 bucket."""
    try:
    # Serialize the DataFrame to Parquet format in-memory
        s3_folder = "qa-agent"
        filename = str(ObjectId()) + '.xlsx' #creates random file name
        s3_key = f"{s3_folder}/{filename}"
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Main Data")
            if extract_data!='':
                extract_data['resource_breakdown'].to_excel(writer, index=False, sheet_name="Resource Breakdown")
                extract_data['third_party_summary'].to_excel(writer, index=False,sheet_name="Third-Party Scripts Summary")
                extract_data['issues'].to_excel(writer,index=False,sheet_name='Potential Issues')
                extract_data['core_web_vitals'].to_excel(writer,index=False,sheet_name='Core Web Vitals')
                extract_data['performance_opportunities'].to_excel(writer,index=False,sheet_name='Performance Opportunities')
                extract_data['performance_details'].to_excel(writer,index=False,sheet_name='Performance Details')
        excel_buffer.seek(0) 
        client_service = ClientService()
        s3_client = client_service.client_type.client
        bucket_name = client_service.client_type.bucket_name
        cdn_url = client_service.client_type.cdn_url
        s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=excel_buffer.getvalue())  
        logger.info(f"Successfully uploaded to s3://{bucket_name}/{s3_key}")
        return cdn_url+"/"+s3_key
    except Exception as e:
        logger.error(
            f"Error executing Uploading the file: {e}",
            extra={"tags": {"task_function": "upload_stream_to_s3"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

class URLCheckerService:
    """
    Service to check the validity of URLs.
    """
    def __init__(self, base_name: str):
        self.base_name = base_name
        self.urls = self.generate_urls()
     

    def generate_urls(self):
        """Generate full URL variants with http/https and optional www."""
        try:
            # Ensure valid parsing by forcing a scheme
            temp_url = self.base_name
            if not temp_url.startswith(("http://", "https://")):
                temp_url = "http://" + temp_url

            parsed = urlparse(temp_url)
            extracted = tldextract.extract(parsed.netloc)

            domain = f"{extracted.domain}.{extracted.suffix}"
            subdomain = extracted.subdomain
            full_domain = domain if not subdomain or subdomain == "www" else f"{subdomain}.{domain}"

            path_and_query = parsed.path or ""
            if parsed.query:
                path_and_query += f"?{parsed.query}"

            urls = []
            prefixes = ["http://", "https://", "http://www.", "https://www."]

            for prefix in prefixes:
                if "www." in prefix:
                    if subdomain == "www":
                        full_host = domain
                    elif subdomain:
                        full_host = f"www.{subdomain}.{domain}"
                    else:
                        full_host = f"www.{domain}"
                else:
                    full_host = full_domain
                urls.append(f"{prefix}{full_host}{path_and_query}")

            logger.info(f"Generated URLs: {urls}")
            return urls
        except Exception as e:
            logger.error(f"Error generating URLs: {e}")
            return []
        
    def is_host_resolvable(self, url: str) -> bool:
        """Check if the hostname in the URL resolves via DNS."""
        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            socket.gethostbyname(hostname)
            return True
        except Exception as e:
            return False
        
    async def check_url_status(self, session, url):
        """Asynchronously check if a URL is reachable."""
        try:

            user_agents = get_user_agents()
            if not self.is_host_resolvable(url):
                return url, False ,None
            try:
                for headers in user_agents:
                    async with session.get(url, headers=headers, timeout=5, allow_redirects=True) as response:
                        if response.status == 200:
                            return url, True , 'crawler_allowed'
                        elif response.status in [403] and response.headers.get('Server') == "cloudflare":
                            logger.warning(f"Cloudflare protection detected for {url} with User-Agent: {headers['User-Agent']}")
                            return url, True ,'crawler_blocker'
                        else:
                            logger.warning(f"URL returned status {response.status} with User-Agent: {headers['User-Agent']}: {url}")
                            return url, False , None
                else:
                    logger.error(f"Failed to retrieve content from {url} with all provided User-Agents")
                    return url, False , None
            except Exception as e:
                logger.error(f"Critical error while checking URL {url}: {e}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while checking {url}: {e}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout while checking {url}")
        except Exception as e:
            logger.error(f"Unexpected error while checking {url}: {e}")
        return url, False , None
    
    async def check_url(self, session, url):
        """Asynchronously check if a URL is reachable."""
        try:

            user_agents = get_user_agents()
            if not self.is_host_resolvable(url):
                return url, False
            try:
                for headers in user_agents:
                    async with session.get(url, headers=headers, timeout=5, allow_redirects=True) as response:
                        if response.status == 200:
                            return url, True
                        else:
                            logger.warning(f"URL returned status {response.status} with User-Agent: {headers['User-Agent']}: {url}")
                else:
                    logger.error(f"Failed to retrieve content from {url} with all provided User-Agents")
            except Exception as e:
                logger.error(f"Critical error while checking URL {url}: {e}")
        except aiohttp.ClientError as e:
            logger.error(f"Network error while checking {url}: {e}")
        except asyncio.TimeoutError:
            logger.error(f"Timeout while checking {url}")
        except Exception as e:
            logger.error(f"Unexpected error while checking {url}: {e}")
        return url, False

    async def check_urls_async(self):
        """Check multiple URLs concurrently."""
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [self.check_url(session, url) for url in self.urls]
                results = await asyncio.gather(*tasks)

                urls = [url for url, status in results if status]
                reachable = sorted(urls, key=lambda x: (x.startswith('http://'), x))
                not_reachable = [url for url, status in results if not status]

                return reachable, not_reachable
        except Exception as e:
            logger.critical(f"Critical error in check_urls_async: {e}")
            return [], []
        

    async def check_urls_async_status(self):
        """Check multiple URLs concurrently."""
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [self.check_url_status(session, url) for url in self.urls]
                results = await asyncio.gather(*tasks)
                result_dict = {}

                for url, status, reason in results:
                    if status or reason == 'crawler_blocker' or reason == 'crawler_allowed':
                        result_dict[url] = reason or "reachable"
    

                return result_dict
        except Exception as e:
            logger.critical(f"Critical error in check_urls_async_status: {e}")
            return {}

def extract_google_genai_error_message(error_message):
    try:
        # Isolate the part after the square bracket containing 'message'
        message_part = error_message.split('message: "', 1)[1]
        # Extract the message before the next double quote
        error_content = message_part.split('"')[0]
        return error_content
    except Exception as e:
        logger.error(f"Failed to extract google GenAI error message: {e}")
        return "An unknown error occurred"

def extract_google_error_message(error_message):
    try:
        # Regex to extract the exception name (e.g., 'NotFound')
        # exception_match = re.search(r"exceptions\.(\w+)", error_message)
        # exception_name = exception_match.group(1) if exception_match else "UnknownException"
        
        # Regex to extract the message inside the parentheses
        message_match = re.search(r"\('([^']+?)(?:\. |$)", error_message)
        
        if message_match:
            extracted_message = message_match.group(1)
        else:
            extracted_message = "An unknown error message"
        
        return extracted_message
    except Exception as e:
        logger.error(f"Failed to extract GenAI error message: {e}")
        return "An unknown error occurred", None






def minify_text(content: str, url: str) -> str:
    """Minifies HTML, CSS, JS, or TXT based on file extension in URL."""
    ext = os.path.splitext(url)[1].lower()

    # CSS
    if ext == ".css":
        # strip /* … */ comments
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        # collapse whitespace
        content = re.sub(r'\s+', ' ', content)
        # remove space around punctuation
        content = re.sub(r'\s*([{};:,>+~])\s*', r'\1', content)

    # JavaScript
    elif ext == ".js":
        # strip //… and /*…*/ comments 
        content = re.sub(r'//.*?(?=\n)|/\*.*?\*/', '', content, flags=re.DOTALL)
        # collapse whitespace
        content = re.sub(r'\s+', ' ', content)
        # tighten up around operators & punctuation
        content = re.sub(r'\s*([{};=(),+\-*/<>?:&|~\[\]])\s*', r'\1', content)

    # HTML, PHP, TXT (generic text)
    elif ext in (".html", ".htm", ".php", ".txt"):
        # strip HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        # collapse between tags
        content = re.sub(r'>\s+<', '><', content)
        # collapse remaining whitespace
        content = re.sub(r'\s+', ' ', content)

    # fallback: collapse runs of whitespace
    else:
        content = re.sub(r'\s+', ' ', content)

    return content.strip()


def is_valid_resource(url_value):
    """Checks if a resource URL is valid."""
    return bool(url_value) and not url_value.startswith(("data:", "javascript:", "#"))


async def fetch_resource_text(session, resource_url):
    """Fetches text content of a resource asynchronously."""
    user_agents = get_user_agents()
    for headers in user_agents:
        try:
            async with session.get(resource_url, headers=headers, timeout=30) as response:
                if response.status == 200:
                    content_type = response.headers.get("Content-Type", "").lower()
                    if "text" in content_type or any(ext in resource_url for ext in [".html", ".css", ".js", ".php",".txt"]):
                        text=await response.text()
                        return minify_text(text, resource_url)
                else:
                    logger.warning(f"Failed {resource_url} with {headers['User-Agent']} - Status: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching {resource_url} with {headers['User-Agent']}: {e}")
    return None



async def process_css_text(session, css_text, base_url):
    imports = re.findall(r'@import\s+["](.+?)["]', css_text)
    for import_url in imports:
        full_url = urljoin(base_url, import_url)
        imported_css = await fetch_resource_text(session, full_url)
        if imported_css:
            css_text += await process_css_text(session, imported_css, full_url)
    return css_text


async def clean_svg_tags(soup):
    try:
        # Remove entire tags named 'pathd' or 'path' with 'd' attribute
        for tag in soup.find_all(['pathd', 'path']):
            if tag.name == 'pathd' or (tag.name == 'path' and tag.has_attr('d')):
                tag.decompose()

        # Remove 'points' attribute from polygon and polyline
        for tag in soup.find_all(['polygon', 'polyline']):
            if tag.has_attr('points'):
                del tag['points']

        # Remove shape-defining attributes from other SVG shapes without deleting tags
        shape_attrs = {
            'circle': ['cx', 'cy', 'r'],
            'rect': ['x', 'y', 'width', 'height', 'rx', 'ry'],
            'ellipse': ['cx', 'cy', 'rx', 'ry'],
            'line': ['x1', 'y1', 'x2', 'y2']
        }

        for shape, attrs in shape_attrs.items():
            for tag in soup.find_all(shape):
                for attr in attrs:
                    if tag.has_attr(attr):
                        del tag[attr]

    except Exception as e:
        print(f"Error occurred while cleaning SVG tags: {e}")
        pass

    # Get updated HTML after removals
    html_text = str(soup)
   
    return html_text,soup


async def scrape_whole_website(url):
    """Fetches the main HTML content and associated text resources asynchronously."""
    combined_text = ""
    async with aiohttp.ClientSession() as session:
        html_text = await fetch_resource_text(session, url)
        if not html_text:
            return f"Error fetching main URL {url}"
        soup = BeautifulSoup(html_text, 'html.parser')
        html_text,soup=await clean_svg_tags(soup=soup)
        combined_text += f"\n\n===== HTML from {url} START =====\n\n{html_text}\n\n===== HTML from {url} END =====\n\n"


        resource_urls = {urljoin(url, tag[attr]) for tag in soup.find_all(True) for attr in ['src', 'href'] if is_valid_resource(tag.get(attr))}
        
        tasks = []
        resource_urls = [url for url in resource_urls if not re.search(r"/(plugins|uploads|cdn[^/]*)/", url)]
        for res_url in resource_urls:
            ext = os.path.splitext(urlparse(res_url).path)[1].lower()
            if ext in [".html", ".css", ".js", ".php"]:
                if urlparse(res_url).netloc == urlparse(url).netloc:  # Check if the domain matches
                    tasks.append(fetch_resource_text(session, res_url))
        
        results = await asyncio.gather(*tasks)
        for res_url, res_text in zip(resource_urls, results):
            if res_text:
                ext = os.path.splitext(urlparse(res_url).path)[1].lower()
                if ext == ".css":
                    res_text = await process_css_text(session, res_text, res_url)
                combined_text += f"\n\n===== FILE from {res_url} START =====\n\n{res_text}\n\n===== FILE from {res_url} END =====\n\n"
        robots_url = urljoin(url, "/robots.txt")
        robots_text = await fetch_resource_text(session, robots_url)
        if robots_text:
            combined_text += f"\n\n===== ROBOTS.TXT from {robots_url} START =====\n\n{robots_text}\n\n===== ROBOTS.TXT from {robots_url} END =====\n\n"
        else:
            combined_text += f"\n\n===== ROBOTS.TXT from {robots_url} NOT FOUND =====\n\n"
            # Check for sitemap files
        potential_sitemaps = [
            "sitemap.xml",
            "sitemap_index.xml",
            "sitemapindex.xml",
            "sitemaps/sitemapindex.xml"
        ]
        sitemap_urls = [urljoin(url, sitemap) for sitemap in potential_sitemaps]
        for sitemap_url in sitemap_urls:
            async with session.get(sitemap_url, timeout=10) as response:
                if response.status == 200:
                    combined_text += f"\n\n===== SITEMAP from {sitemap_url} AVAILABLE =====\n\n"
                else:
                    combined_text += f"\n\n===== SITEMAP from {sitemap_url} NOT FOUND =====\n\n"
        combined_text = re.sub(r'\("path",\{[^{}]*d\s*:\s*"[^"]*"[^{}]*\}\)', '', combined_text)
        combined_text = re.sub(r'\{tag\s*:\s*"path"\s*,\s*attr\s*:\s*\{[^{}]*d\s*:\s*"[^"]*"[^{}]*\},\s*child\s*:\s*\[\]\},?', '', combined_text)
        combined_text = re.sub(r'<path\b[^>]*\bd="[^"]*Z"\s*/?>', '', combined_text)
        combined_text = re.sub(r'<path[^>]*\sd="[^"]+"[^>]*/?>', '', combined_text) 
        combined_text = re.sub(r'\s*points="[^"]*"', '', combined_text)
    return combined_text


async def extract_data(mobile_data, desktop_data):
    async def format_size(size):
        if size >= 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        return f"{size / 1024:.0f} KB"

    async def classify_rating(metric, value):
        thresholds = {
            "FCP": {"fast": 1800, "average": 3000},
            "LCP": {"fast": 2500, "average": 4000},
            "CLS": {"fast": 0.1, "average": 0.25},
            "INP": {"fast": 200, "average": 500},
            "TTFB": {"fast": 800, "average": 1800}
        }
        if value <= thresholds[metric]["fast"]:
            return "✅"
        elif value <= thresholds[metric]["average"]:
            return "⚠️"
        return "❌"

    async def extract_resource_breakdown():
        mobile_resources = mobile_data.get("lighthouseResult", {}).get("audits", {}).get("resource-summary", {}).get("details", {}).get("items", [])
        desktop_resources = desktop_data.get("lighthouseResult", {}).get("audits", {}).get("resource-summary", {}).get("details", {}).get("items", [])
        extracted_data = []
        resource_types = set(item.get("label", "Unknown") for item in mobile_resources + desktop_resources)
        for resource_type in resource_types:
            mobile_item = next((item for item in mobile_resources if item.get("label") == resource_type), {})
            desktop_item = next((item for item in desktop_resources if item.get("label") == resource_type), {})
            mobile_requests = mobile_item.get("requestCount", 0)
            mobile_transfer_size = await format_size(mobile_item.get('transferSize', 0))
            desktop_requests = desktop_item.get("requestCount", 0)
            desktop_transfer_size = await format_size(desktop_item.get('transferSize', 0))
            extracted_data.append([resource_type, mobile_requests, mobile_transfer_size, desktop_requests, desktop_transfer_size])
        headers = ["Type", "Mobile Requests", "Mobile Transfer Size", "Desktop Requests", "Desktop Transfer Size"]
        return pd.DataFrame(extracted_data, columns=headers)

    async def extract_third_party_summary():
        mobile_third_party = mobile_data.get("lighthouseResult", {}).get("audits", {}).get("third-party-summary", {}).get("details", {}).get("items", [])
        desktop_third_party = desktop_data.get("lighthouseResult", {}).get("audits", {}).get("third-party-summary", {}).get("details", {}).get("items", [])
        extracted_data = []
        providers = set(item.get("entity", "Unknown Provider") for item in mobile_third_party + desktop_third_party)
        for provider in providers:
            mobile_item = next((item for item in mobile_third_party if item.get("entity") == provider), {})
            desktop_item = next((item for item in desktop_third_party if item.get("entity") == provider), {})
            mobile_transfer_size = f"{mobile_item.get('transferSize', 0) // 1024} KB"
            mobile_blocking_time = f"{mobile_item.get('blockingTime', 0)} ms"
            desktop_transfer_size = f"{desktop_item.get('transferSize', 0) // 1024} KB"
            desktop_blocking_time = f"{desktop_item.get('blockingTime', 0)} ms"
            extracted_data.append([provider, mobile_transfer_size, mobile_blocking_time, desktop_transfer_size, desktop_blocking_time])
        headers = ["Provider", "Mobile Transfer Size", "Mobile Blocking Time", "Desktop Transfer Size", "Desktop Blocking Time"]
        return pd.DataFrame(extracted_data, columns=headers)

    async def extract_issues():
        categories = ["accessibility", "seo", "best-practices"]
        extracted_data = []
        for category in categories:
            mobile_audits = mobile_data.get("lighthouseResult", {}).get("audits", {})
            desktop_audits = desktop_data.get("lighthouseResult", {}).get("audits", {}) if desktop_data else {}
            for audit_key, audit_value in mobile_audits.items():
                score = audit_value.get("score")
                if score is not None and score < 1:
                    title = audit_value.get("title", "Unknown Issue")
                    affected_elements = audit_value.get("details", {}).get("items", "N/A")
                    fix_suggestion = audit_value.get("description", "No fix suggestion available")
                    desktop_fix = "N/A"
                    if audit_key in desktop_audits:
                        desktop_score = desktop_audits[audit_key].get("score")
                        if desktop_score is not None and desktop_score < 1:
                            desktop_fix = desktop_audits[audit_key].get("description", "No fix suggestion available")
                    extracted_data.append({
                        "Category": category.capitalize(),
                        "Title": title,
                        "Affected Elements": affected_elements,
                        "Mobile Fix Suggestion": fix_suggestion,
                        "Desktop Fix Suggestion": desktop_fix
                    })
        return pd.DataFrame(extracted_data)

    async def extract_core_web_vitals():
        metrics = ["first-contentful-paint", "largest-contentful-paint", "cumulative-layout-shift", "interaction-to-next-paint", "server-response-time"]
        display_names = {"first-contentful-paint": "FCP", "largest-contentful-paint": "LCP", "cumulative-layout-shift": "CLS", "interaction-to-next-paint": "INP", "server-response-time": "TTFB"}
        mobile_audits = mobile_data.get("lighthouseResult", {}).get("audits", {})
        desktop_audits = desktop_data.get("lighthouseResult", {}).get("audits", {})
        extracted_data = []
        for metric in metrics:
            mobile_value = mobile_audits.get(metric, {}).get("numericValue", 0)
            desktop_value = desktop_audits.get(metric, {}).get("numericValue", 0)
            mobile_rating = await classify_rating(display_names[metric], mobile_value)
            desktop_rating = await classify_rating(display_names[metric], desktop_value)
            extracted_data.append([display_names[metric], f"{mobile_value} ms", mobile_rating, f"{desktop_value} ms", desktop_rating])
        headers = ["Metric", "Mobile Value", "Mobile Rating", "Desktop Value", "Desktop Rating"]
        return pd.DataFrame(extracted_data, columns=headers)

    async def extract_warning_performance_opportunities():
        async def extract_opportunities(audits):
            extracted = []
            for key, audit in audits.items():
                score = audit.get("score", 1)
                if score is not None and isinstance(score, (int, float)) and score < 1:
                    title = audit.get("title", "Unknown Issue")
                    savings = audit.get("displayValue") or audit.get("details", {}).get("overallSavingsMs") or "No specific savings"
                    extracted.append(f"⚠️ {title} – {savings}")
            return extracted
        mobile_audits = mobile_data.get("lighthouseResult", {}).get("audits", {})
        desktop_audits = desktop_data.get("lighthouseResult", {}).get("audits", {}) if desktop_data else {}
        mobile_opportunities = await extract_opportunities(mobile_audits)
        desktop_opportunities = await extract_opportunities(desktop_audits)
        opportunities_data = {
            "Device": ["Mobile"] * len(mobile_opportunities) + ["Desktop"] * len(desktop_opportunities),
            "Opportunity": mobile_opportunities + desktop_opportunities
        }
        return pd.DataFrame(opportunities_data)
    
    async def extract_performance_opportunities():
        opportunities = []
        
        async def extract_opportunities(audits, device_type):
            extracted = []
            for key, audit in audits.items():
                if not isinstance(audit, dict):
                    continue

                details = audit.get("details", {})

                # Identify opportunities based on score or ID containing "opportunity"
                if (audit.get("scoreDisplayMode") == "numeric" and float(audit.get("score", 1)) < 1) or "opportunity" in audit.get("id", "").lower():
                    opportunity = {
                        "device": device_type,
                        "title": audit.get("title", "Unknown"),
                        "description": audit.get("description", "No description available"),
                        "score": audit.get("score", "N/A"),
                        "savings": audit.get("displayValue", "N/A")
                    }

                    # Extract problematic items
                    items = details.get("items", [])
                    problematic_items = []
                    for item in items:
                        if not isinstance(item, dict):
                            continue

                        try:
                            url = item.get("url") or item.get("source") or item.get("request") or ""
                            size = item.get("totalBytes") or item.get("wastedBytes") or 0
                            wasted = item.get("wastedBytes") or item.get("wastedMs") or 0

                            if url:
                                item_str = f"- {url}"
                                if size:
                                    item_str += f" (Size: {size // 1024} KB"
                                    if wasted:
                                        item_str += f", Waste: {wasted // 1024} KB"
                                    item_str += ")"
                                problematic_items.append(item_str)
                        except (TypeError, AttributeError) as e:
                            print(f"Warning: Error processing item: {e}")
                            continue

                    if problematic_items:
                        opportunity["problematic_items"] = problematic_items

                    extracted.append(opportunity)
            
            return extracted
        
        # Extract data for both mobile and desktop
        mobile_opportunities = await extract_opportunities(mobile_data.get("lighthouseResult", {}).get("audits", {}), "Mobile")
        desktop_opportunities = await extract_opportunities(desktop_data.get("lighthouseResult", {}).get("audits", {}), "Desktop") if desktop_data else []
        if isinstance(desktop_opportunities, list) and isinstance(mobile_opportunities, list):
            all_opportunities = desktop_opportunities + mobile_opportunities
            df = pd.DataFrame(all_opportunities)
        return df
    resource_breakdown = await extract_resource_breakdown()
    third_party_summary = await extract_third_party_summary()
    issues = await extract_issues()
    core_web_vitals = await extract_core_web_vitals()
    performance_opportunities = await extract_warning_performance_opportunities()
    performance_details = await extract_performance_opportunities()

    return {
        "resource_breakdown": resource_breakdown,
        "third_party_summary": third_party_summary,
        "issues": issues,
        "core_web_vitals": core_web_vitals,
        "performance_opportunities": performance_opportunities,
        "performance_details":performance_details
    }


async def assign_tag(value, thresholds):
    if value <= thresholds[0]:
        return "Green (fast)"
    elif value <= thresholds[1]:
        return "Orange (moderate)"
    return "Red (slow)"

async def assign_score_tag(score):
    if score < 50:
        return "Fail"
    elif score < 90:
        return "Warning"
    return "Pass"

async def assign_cls_tag(value):
    if value < 0.1:
        return "Good"
    elif value <= 0.25:
        return "Needs Improvements"
    return "Poor"


# Function to extract relevant data from JSON
async def extract_metrics(data, device_type):
    thresholds = {
        "FCP": [0.9, 1.6] if device_type == "desktop" else [1.8, 3],
        "LCP": [1.2, 2.4] if device_type == "desktop" else [2.5, 4],
        "TBT": [150, 350] if device_type == "desktop" else [200, 600],
        "SpeedIndex": [1.3, 2.3] if device_type == "desktop" else [3.4, 5.8]
    }
    performance_score = round(data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", 0) * 100)
    accessibility_score = round(data.get("lighthouseResult", {}).get("categories", {}).get("accessibility", {}).get("score", 0) * 100)
    best_practices_score = round(data.get("lighthouseResult", {}).get("categories", {}).get("best-practices", {}).get("score", 0) * 100)
    seo_score = round(data.get("lighthouseResult", {}).get("categories", {}).get("seo", {}).get("score", 0) * 100)

    fcp = round(data.get("lighthouseResult", {}).get("audits", {}).get("first-contentful-paint", {}).get("numericValue", 0) / 1000, 1)
    lcp = round(data.get("lighthouseResult", {}).get("audits", {}).get("largest-contentful-paint", {}).get("numericValue", 0) / 1000, 1)
    tbt = round(data.get("lighthouseResult", {}).get("audits", {}).get("total-blocking-time", {}).get("numericValue", 0), 1)
    cls = round(data.get("lighthouseResult", {}).get("audits", {}).get("cumulative-layout-shift", {}).get("numericValue", 0), 1)
    speed_index = round(data.get("lighthouseResult", {}).get("audits", {}).get("speed-index", {}).get("numericValue", 0) / 1000, 1)
    ttfb_value = data.get("loadingExperience", {}).get("metrics", {}).get("EXPERIMENTAL_TIME_TO_FIRST_BYTE", {}).get("percentile", "N/A")
    ttfb = {
        "value": round(ttfb_value / 1000, 1) if ttfb_value != "N/A" else "N/A",
        "tag": data.get("loadingExperience", {}).get("metrics", {}).get("EXPERIMENTAL_TIME_TO_FIRST_BYTE", {}).get("Category", "N/A"),
        "unit": "SECONDS" if ttfb_value != "N/A" else "N/A"
    }
    inp_value = data.get("loadingExperience", {}).get("metrics", {}).get("INTERACTION_TO_NEXT_PAINT", {}).get("percentile", "N/A")
    inp = {
        "value": inp_value,
        "tag": data.get("loadingExperience", {}).get("metrics", {}).get("INTERACTION_TO_NEXT_PAINT", {}).get("Category", "N/A"),
        "unit": "MILLISECONDS" if inp_value != "N/A" else "N/A"
    }
    status_mapping = {
        "SLOW": "Failed",
        "FAST": "Passed",
    }
    return {
        "Core Web Vitals Assessment": status_mapping.get(data.get("loadingExperience", {}).get("overall_category", "").upper(), "Warning"),
        "Metrics": {
            "Largest Contentful Paint (LCP)": {"value": lcp, "tag": await assign_tag(lcp, thresholds["LCP"]),"unit":"SECONDS"},
            "Interaction to Next Paint (INP)": inp,
            "Cumulative Layout Shift (CLS)": {"value": cls, "tag": await assign_cls_tag(cls)},
            "First Contentful Paint (FCP)": {"value": fcp, "tag": await assign_tag(fcp, thresholds["FCP"]),"unit":"SECONDS"},
            "Time to First Byte (TTFB)": ttfb,
        },
        "Diagnose Performance Issues": {
            "Performance": {"score": performance_score, "tag": await assign_score_tag(performance_score)},
            "Accessibility": {"score": accessibility_score, "tag": await assign_score_tag(accessibility_score)},
            "Best Practices": {"score": best_practices_score, "tag": await assign_score_tag(best_practices_score)},
            "SEO": {"score": seo_score, "tag": await assign_score_tag(seo_score)},
            "Total Blocking Time": {"value": tbt, "tag": await assign_tag(tbt, thresholds["TBT"]),"unit":"MILLISECONDS"},
            "Speed Index": {"value": speed_index, "tag": await assign_tag(speed_index, thresholds["SpeedIndex"]),"unit":"SECONDS"},
        },
    }

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class GeminiAPIKeyManager(metaclass=Singleton):
    def __init__(self, api_key_details=None, reset_interval=60):
        """
        Initialize the GeminiAPIKeyManager with round-robin access and periodic reset.

        :param api_key_details: Dictionary of API keys (name -> encrypted key).
        :param reset_interval: Interval (in seconds) to reset key usage tracking.
        """
        self.api_keys = api_key_details or {}
        self.api_keys = {f"key{i+1}": v for i, v in enumerate(api_key_details)}
        self.api_key_list = list(self.api_keys.keys())
        self.key_usage = {key: 0 for key in self.api_keys.keys()}
        self.current_index = 0
        self.lock = Lock()
        self.reset_interval = reset_interval

        # Start background thread to reset key usage periodically
        self.reset_thread = Thread(target=self._reset_key_usage, daemon=True)
        self.reset_thread.start()

    def get_api_key(self):
        """
        Return the next API key in round-robin order and increment its usage counter.

        :return: Decrypted API key string.
        """
        with self.lock:
            if not self.api_key_list:
                raise ValueError("No Gemini API keys available.")

            key_name = self.api_key_list[self.current_index]
            encrypted_key = self.api_keys[key_name]

            # Rotate to the next key
            self.current_index = (self.current_index + 1) % len(self.api_key_list)

            # Track usage
            self.key_usage[key_name] += 1

            return decryptor.decrypt(encrypted_key)

    def _reset_key_usage(self):
        """
        Background thread to reset key usage stats at the given interval.
        """
        while True:
            time.sleep(self.reset_interval)
            with self.lock:
                self.key_usage = {key: 0 for key in self.api_keys.keys()}
                self.current_index = 0  # Optional: reset to start from key1 again





def split_by_token_limit(text, max_tokens, encoding_name="gpt2"):
    """
    Splits text into chunks <= max_tokens. Prefers paragraph-based splitting.
    If a paragraph exceeds max_tokens, splits it by tokens directly.
    """
    encoding = get_cached_encoding(encoding_name)
    paragraphs = text.split("\n")
    chunks = []
    current_chunk = ""
    current_tokens = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_tokens = encoding.encode(para)
        para_token_count = len(para_tokens)

        if para_token_count > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_tokens = 0

            start = 0
            while start < para_token_count:
                end = start + max_tokens
                chunk_tokens = para_tokens[start:end]
                chunk_text = encoding.decode(chunk_tokens)
                chunks.append(chunk_text.strip())
                start = end
        else:
            if current_tokens + para_token_count > max_tokens:
                chunks.append(current_chunk.strip())
                current_chunk = para
                current_tokens = para_token_count
            else:
                current_chunk += ("\n" if current_chunk else "") + para
                current_tokens += para_token_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def split_and_write_text_by_token_limit(combined_text: str, token_limit: int, encoding_name="gpt2"):
    """
    Splits text by top-level sections and token limit.
    Falls back to paragraph-based or token-based splitting when needed.
    """
    encoding = get_cached_encoding(encoding_name)
    sections = combined_text.split("\n===== ")

    chunks = []
    current_chunk = ""
    current_tokens = 0

    for i, section in enumerate(sections):
        if not section.strip():
            continue

        section_text = section if i == 0 else "\n===== " + section
        section_tokens = encoding.encode(section_text)
        section_token_count = len(section_tokens)

        if section_token_count > token_limit:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_tokens = 0

            section_chunks = split_by_token_limit(section_text, token_limit, encoding_name)
            chunks.extend(section_chunks)
        else:
            if current_tokens + section_token_count > token_limit:
                chunks.append(current_chunk.strip())
                current_chunk = section_text
                current_tokens = section_token_count
            else:
                current_chunk += section_text
                current_tokens += section_token_count

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Load encrypted Gemini keys from settings
settings_pro_agent_data = get_field_by_name('setting', 'QA_AGENT', 'details')
gemini_key_details = settings_pro_agent_data.get("gemini_key", {})
gemini_key_manager = GeminiAPIKeyManager(gemini_key_details, reset_interval=60)