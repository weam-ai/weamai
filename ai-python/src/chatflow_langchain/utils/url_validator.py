import pandas as pd
from src.logger.default_logger import logger
import os
import io
import aiohttp
import asyncio
import tldextract
from src.chatflow_langchain.utils.user_agents import get_user_agents
from urllib.parse import urljoin, urlparse
import socket
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

    async def check_url(self, session, url):
        """Asynchronously check if a URL is reachable."""
        try:
            user_agents = get_user_agents()
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
                logger.warning(f"Site not reachable or unavailable for URL: {url}. Error: {e}")
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

    async def check_urls_async_status(self):
        """Check multiple URLs concurrently."""
        try:
            async with aiohttp.ClientSession() as session:
                tasks = [self.check_url_status(session, url) for url in self.urls]
                results = await asyncio.gather(*tasks)
                result_dict = {}

                for url, status, reason in results:
                    if status and reason in {'crawler_blocker', 'crawler_allowed'}:
                        result_dict[url] = {"status": status,"reason": reason if reason else "reachable"}

                return result_dict
        except Exception as e:
            logger.critical(f"Critical error in check_urls_async_status: {e}")
            return {}