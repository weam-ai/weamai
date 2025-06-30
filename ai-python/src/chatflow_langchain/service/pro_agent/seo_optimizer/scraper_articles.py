import requests
from typing import List, Dict, Tuple
import os
import openai
import json
from typing import List, Optional
from newspaper import Article
from bs4 import BeautifulSoup
import pyhtml2md
import statistics
from src.chatflow_langchain.utils.user_agents import get_user_agents
import aiohttp
import asyncio
from src.logger.default_logger import logger
from src.chatflow_langchain.service.pro_agent.seo_optimizer.utils import is_probable_blog_url
from dotenv import load_dotenv
import tiktoken
import gc
load_dotenv()

class ArticleFetcher:
    def __init__(self):
        self.username=os.environ.get("SEO_USER_ID")
        self.password=os.environ.get("SEO_PASSWORD")
        self.serp_api_url = "https://api.dataforseo.com/v3/serp/google/organic/live/regular"
        self.word_count_api_url = "https://api.dataforseo.com/v3/on_page/instant_pages"
        self.headers = {"Content-Type": "application/json"}
        self.response_headers='text/html'

    async def initialize_data(self, title: str=None, location: list=None, language: str=None):
        self.title = title
        self.location = location
        self.language = language
    
    async def get_articles_by_title(self, title: str) -> List[str]:
        payload = [{
            "keyword": title,
            "language_name": self.language,
            "location_name": self.location[0],
            "device": "desktop",
            "depth":5
        }]

        
        response = requests.post(self.serp_api_url, auth=(self.username, self.password), json=payload, headers=self.headers)
        if response.status_code == 200:
            results = response.json()
            article_urls = [
                item["url"]
                for item in results.get("tasks", [])[0].get("result", [])[0].get("items", [])
                if is_probable_blog_url(item["url"])
            ]
            return article_urls
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []

    async def get_word_count(self, url: str) -> int:
        payload = [{
            "url": url,
            "enable_javascript": True
        }]

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.word_count_api_url,
                    auth=aiohttp.BasicAuth(self.username, self.password),
                    json=payload,
                    headers=self.headers,
                    timeout=30
                ) as response:
                    if response.status == 200:
                        results = await response.json()
                        tasks = results.get("tasks", [])
                        if tasks:
                            result = tasks[0].get("result", [])
                            if result:
                                items = result[0].get("items", [])
                                if items:
                                    meta = items[0].get("meta", {})
                                    content = meta.get("content", {})
                                    return content.get("plain_text_word_count", 0)
            except Exception as e:
                logger.error(f"Error fetching word count for {url}: {e}")

        return 0

    async def get_articles_word_count(self, title: str) -> Tuple[int, List[str]]:
        self.top_articles = await self.get_articles_by_title(title)

        async def fetch_word_count(url: str):
            word_count = await self.get_word_count(url)
            return url, word_count

        tasks = [fetch_word_count(url) for url in self.top_articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        article_word_counts = {}
        word_count_list = []

        for result in results:
            if isinstance(result, tuple):
                url, word_count = result
                article_word_counts[url] = word_count
                word_count_list.append(word_count)
            else:
                logger.error(f"Error fetching word count: {result}")

        median_length = statistics.median(word_count_list) if word_count_list else 600

        return median_length, self.top_articles

    async def fetch_article_content(self) -> str:
        """Fetch article content from multiple URLs."""
        all_articles = []
        formatted_articles=[]
        for url in self.top_articles:
            try:
                article = Article(url)
                article.download()
                article.parse()
                soup = BeautifulSoup(article.html, 'html.parser')
                body = soup.body
                # extracted_html = soup.prettify()  # Cleaned HTML
                

                # Convert HTML to Markdown
                markdown_text = pyhtml2md.convert(str(body))

                all_articles.append({
                    "URL": url,
                    "Title": article.title,
                    "Body Content": markdown_text
                })
                content=f"Source: {url}\nTitle: {article.title}\nContent: {markdown_text}\n\n"
                formatted_articles.append(content)
        
            except Exception as e:
                error_content=str(e)
                error_content=f"Source: {url}\n \Error: {error_content}\n\n"
                formatted_articles.append(error_content)

        combined_content="\n".join(formatted_articles)

        return combined_content.replace("{", "{{").replace("}", "}}")
    
    async def fetch_article_content_beautifulsoup(self) -> str:
        formatted_articles = []
        user_agents = get_user_agents()
        combined_tokens = 0
        MAX_CONTENT_LENGTH = 100000  # 100k limit
        async def fetch_content(url: str):
            for headers in user_agents:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url, headers=headers, timeout=30) as response:
                            if response.status == 200 and response.headers.get('Content-Type', '').startswith('text/html'):
                                text = await response.text()
                                soup = BeautifulSoup(text, "html.parser")

                                # Remove unwanted tags
                                for tag in soup.find_all(["script", "style", "header", "footer", "nav", "aside", "svg"]):
                                    tag.decompose()

                                # Remove inline styles and JS-related attributes
                                for tag in soup.find_all(True):
                                    attrs_to_remove = [attr for attr in tag.attrs if attr.lower().startswith("on") or attr.lower() in ("style", "class", "id")]
                                    for attr in attrs_to_remove:
                                        del tag.attrs[attr]

                                # Extract title
                                title = soup.title.string.strip() if soup.title and soup.title.string else "No Title Found"

                                # Extract meta description
                                meta_description_tag = soup.find("meta", attrs={"name": "description"})
                                meta_description = meta_description_tag["content"].strip() if meta_description_tag and "content" in meta_description_tag.attrs else "No meta description found"

                                # Extract all meta tags
                                meta_tags = soup.find_all('meta')
                                meta_data = {}
                                for tag in meta_tags:
                                    if 'name' in tag.attrs:
                                        meta_data[tag.attrs['name']] = tag.attrs.get('content', '')
                                    elif 'property' in tag.attrs:
                                        meta_data[tag.attrs['property']] = tag.attrs.get('content', '')

                                # Extract <head> and <body> content
                                head = soup.head
                                body = soup.body
                                head_md = pyhtml2md.convert(str(head)) if head else "No head content"
                                body_md = pyhtml2md.convert(str(body)) if body else "No body content"

                                # Prepare output
                                content = (
                                    f"Source: {url}\n"
                                    f"Title: {title}\n"
                                    f"Meta Description: {meta_description}\n"
                                    f"Meta Tags:\n"
                                )

                                for key, value in meta_data.items():
                                    content += f"{key}: {value}\n"

                                content += (
                                    f"\nHead Content:\n{head_md}\n\n"
                                    f"Body Content:\n{body_md}\n\n"
                                )
                                return content
                            else:
                                logger.error(f"❌ Status {response.status} for {url}")
                except Exception as inner_e:
                    logger.error(f"⚠️ Failed UA {headers['User-Agent']} for {url}: {inner_e}")
            return f"Source: {url}\nError: All User-Agents failed\n\n"

        encoding = tiktoken.get_encoding("cl100k_base")

        for url in self.top_articles:
            article_content = await fetch_content(url)
            content_tokens = len(encoding.encode(article_content))
            proposed_total = combined_tokens + content_tokens

            if proposed_total <= MAX_CONTENT_LENGTH:
                formatted_articles.append(article_content)
                combined_tokens += content_tokens
                logger.info(
                    f"✅ Included: {url}\n"
                    f" → Token count: {content_tokens}\n"
                    f" → Total after inclusion: {combined_tokens}"
                )
            else:
                logger.warning(
                    f"⚠️ Skipped: {url}\n"
                    f" → Token count: {content_tokens}\n"
                    f" → Current total: {combined_tokens}\n"
                    f" → Would exceed {MAX_CONTENT_LENGTH} if included (Total: {proposed_total})"
                )

        combined_content = "\n".join(formatted_articles)

        # Optional: escape curly braces (only needed for template safety)
        combined_filtered_content = combined_content.replace("{", "{{").replace("}", "}}")

        logger.info(f"✅ Successfully fetched content with total tokens: {combined_tokens}")

        del encoding
        gc.collect()
        return combined_filtered_content