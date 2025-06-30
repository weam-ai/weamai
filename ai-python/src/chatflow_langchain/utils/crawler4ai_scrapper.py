from fastapi import HTTPException
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai import CrawlerMonitor, DisplayMode
from src.logger.default_logger import logger
from src.chatflow_langchain.service.pro_agent.qa_special.utils import URLCheckerService
import re
import os
import asyncio
import tldextract
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from src.chatflow_langchain.service.pro_agent.qa_special.utils import is_valid_resource,process_css_text
import aiohttp
class CrawlerService:
    def __init__(self):
        self.config = CrawlerRunConfig(
            word_count_threshold=10,
            excluded_tags=["img", "script", "style"],
            exclude_external_links=True,
            # exclude_social_media_links=True,
            exclude_external_images=True,
            cache_mode=CacheMode.BYPASS
        )

    async def crawl_and_clean(self, url: str) -> str:
        """
        Crawls the provided URL, cleans up the result, and returns the markdown.
        Logs the process for debugging and success tracking.
        Raises HTTPException on errors.
        """
        try:
            logger.info(f"Starting crawl for URL: {url}")
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url, config=self.config)
                markdown = result.markdown

                if not markdown:
                    logger.warning(f"No markdown content found for URL: {url}")
                    raise HTTPException(status_code=400, detail="No content found on the page")

                logger.info(f"Successfully crawled and cleaned URL: {url}")
                return markdown
        except Exception as e:
            logger.error(f"Error during crawl for URL: {url} - {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error during crawl: {str(e)}")
    

    async def multiple_crawl_and_clean(self, urls: list) -> str:
        """
        Crawls the provided URL, cleans up the result, and returns the markdown.
        Logs the process for debugging and success tracking.
        Raises HTTPException on errors.
        """
        dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10,
        )
        try:
            logger.info(f"Starting crawl for URL: {urls}")
            markdown = ""
            reachable_urls = []
            for i in range(len(urls)):
                checker = URLCheckerService(urls[i])
                reachable, not_reachable = await checker.check_urls_async()
                if reachable:
                    reachable_urls.append(reachable[0])
            if len(reachable_urls) > 0:
                async with AsyncWebCrawler() as crawler:
                    result = await crawler.arun_many(urls=reachable_urls, config=self.config,dispatcher=dispatcher)
                    for res in result:
                        markdown += res.markdown

                    if not markdown:
                        logger.warning(f"No markdown content found for URL: {urls}")
                        raise HTTPException(status_code=400, detail="No content found on the page")

                    logger.info(f"Successfully crawled and cleaned URL: {urls}")
            else:
                markdown = ""
            return markdown
        except Exception as e:
            logger.error(f"Error during crawl for URL: {urls} - {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error during crawl: {str(e)}")
        
    async def crawl_and_clean_non_markdown(self, url: str):
        """
        Crawls the provided URL and returns the full crawl result (not just markdown).
        """
        try:
            logger.info(f"Starting crawl for URL: {url}")
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url, config=self.config)

                if not result or not result.markdown:
                    logger.warning(f"No markdown content found for URL: {url}")
                    raise HTTPException(status_code=400, detail="No content found on the page")

                logger.info(f"Successfully crawled and cleaned URL: {url}")
                return result

        except Exception as e:
            logger.error(f"Error during crawl for URL: {url} - {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error during crawl: {str(e)}")
        
    async def crawl_and_clean_external_files(self, urls: str):
        """
        Crawls the provided URL and returns the full crawl result (not just markdown).
        """
        try:
            logger.info(f"Starting crawl for URL: {urls}")
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun_many(urls=urls, config=self.config)


                logger.info(f"Successfully crawled and cleaned URL: {urls}")
                return result

        except Exception as e:
            logger.error(f"Error during crawl for URL: {urls} - {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error during crawl: {str(e)}")
        
    async def crawl_and_clean_qa_agent(self, url: str):
        """
        Crawls the provided URL and returns the full crawl result (not just markdown).
        """
        try:
            logger.info(f"Starting crawl for URL: {url}")
            self.config.excluded_tags = ['svg','circle','rect','ellipse','line','path','polygon','polyline']
            async with AsyncWebCrawler() as crawler:
                result = await crawler.arun(url=url, config=self.config)

                if not result or not result.markdown:
                    logger.warning(f"No markdown content found for URL: {url}")
                    raise HTTPException(status_code=400, detail="No content found on the page")

                logger.info(f"Successfully crawled and cleaned URL: {url}")
                combined_text=""
                soup = BeautifulSoup(result.html, 'html.parser')
                combined_text += f"\n\n===== HTML from {url} START =====\n\n{result.html}\n\n===== HTML from {url} END =====\n\n"


                resource_urls = {urljoin(url, tag[attr]) for tag in soup.find_all(True) for attr in ['src', 'href'] if is_valid_resource(tag.get(attr))}
                
                urls_list = []
                resource_urls = [url for url in resource_urls if not re.search(r"/(plugins|uploads|cdn[^/]*)/", url)]
                for res_url in resource_urls:
                    ext = os.path.splitext(urlparse(res_url).path)[1].lower()
                    if ext in [".html", ".css", ".js", ".php"]:
                        if urlparse(res_url).netloc == urlparse(url).netloc:  # Check if the domain matches
                            urls_list.append(res_url)
                
                results = await self.crawl_and_clean_external_files(urls_list)
                for res_url, res_text in zip(resource_urls, results):
                    if res_text:
                        ext = os.path.splitext(urlparse(res_url).path)[1].lower()
                        if ext == ".css":
                            async with aiohttp.ClientSession() as session:
                                res_text = await process_css_text(session, res_text.html, res_url)
                                combined_text += f"\n\n===== FILE from {res_url} START =====\n\n{res_text}\n\n===== FILE from {res_url} END =====\n\n"
                        else:
                            combined_text += f"\n\n===== FILE from {res_url} START =====\n\n{res_text.html}\n\n===== FILE from {res_url} END =====\n\n"
                robots_url = urljoin(url, "/robots.txt")
                robots_text = await self.crawl_and_clean_external_files([robots_url])
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
                combined_text += f"\n\n===== SITEMAP from {sitemap_urls} FOUND =====\n\n"
                combined_text = re.sub(r'\("path",\{[^{}]*d\s*:\s*"[^"]*"[^{}]*\}\)', '', combined_text)
                combined_text = re.sub(r'\{tag\s*:\s*"path"\s*,\s*attr\s*:\s*\{[^{}]*d\s*:\s*"[^"]*"[^{}]*\},\s*child\s*:\s*\[\]\},?', '', combined_text)
                combined_text = re.sub(r'<path\b[^>]*\bd="[^"]*Z"\s*/?>', '', combined_text)
                combined_text = re.sub(r'<path[^>]*\sd="[^"]+"[^>]*/?>', '', combined_text) 
                combined_text = re.sub(r'\s*points="[^"]*"', '', combined_text)
                return combined_text

        except Exception as e:
            logger.error(f"Error during crawl for URL: {url} - {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error during crawl: {str(e)}")