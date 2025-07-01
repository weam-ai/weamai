import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
import threading
import hashlib
from bson.objectid import ObjectId
from src.db.config import db_instance
from src.chatflow_langchain.repositories.sitemap import SiteMapRepo
from src.chatflow_langchain.service.pro_agent.seo_optimizer.config import SiteMapCollection

class SitemapTitleScraper:
    def __init__(self, data: dict = {}):
        self.website = data.get("website", "")
        self.thread_id = data.get("thread_id", "")
        self.company_id = data.get("company_id", "")
        self.chat_session_id = data.get("chat_session_id", "")
        self.brain_id = data.get("brain_id", "")

        self.sitemap = SiteMapCollection.site_map_collection
        self.db_instance = db_instance
        self.sitemap_instance = db_instance[self.sitemap]
        self.sitemap_repo = SiteMapRepo(collection_name=self.sitemap)
        self.sitemap_repo.initilize_thread_id(thread_id=self.thread_id)
        self.sitemap_repo.initilize_extra_data(extra_data={"website": self.website})

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            )
        }

        self.potential_sitemaps = [
            "sitemap.xml",
            "sitemap_index.xml",
            "sitemapindex.xml",
            "sitemaps/sitemapindex.xml"
        ]

        self.titles = []
        self.title_hashes = []
        self.existing_hashes = set()
        self.semaphore = asyncio.Semaphore(15)  # Limit concurrency

    async def fetch_url(self, session, url):
        try:
            async with session.get(url, headers=self.headers) as response:
                print(f"Fetching {url}, Status: {response.status}")
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def extract_sitemap_links(self, content):
        soup = BeautifulSoup(content, "xml")
        return [loc.text for loc in soup.find_all("loc")]

    async def get_sitemap_urls(self):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_url(session, f"{self.website}/{sitemap}")
                for sitemap in self.potential_sitemaps
            ]
            responses = await asyncio.gather(*tasks)

        list_xml = [
            link
            for response in responses if response
            for link in self.extract_sitemap_links(response)
        ]

        if not list_xml:
            print("No valid sitemap found.")

        final_site_map = []
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_url(session, url) for url in list_xml]
            responses = await asyncio.gather(*tasks)

        for response in responses:
            if response:
                final_site_map += self.extract_sitemap_links(response)

        return [
            url for url in final_site_map
            if "/blog/" in url or "-blog" in url.lower()
        ]

    async def fetch_title(self, session, url):
        async with self.semaphore:  # Limit concurrent fetches
            try:
                async with session.get(url, headers=self.headers) as response:
                    print(f"Fetching {url}, Status: {response.status}")
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, "html.parser")
                        title = soup.find("title").text.strip() if soup.find("title") else "No title found"
                        title_hash = hashlib.sha256(title.encode()).hexdigest()
                        self.titles.append(title)
                        self.title_hashes.append(title_hash)
            except Exception as e:
                print(f"Error fetching title for {url}: {e}")

    async def get_blog_titles(self, blog_urls):
        if not blog_urls:
            print("No blog URLs found.")
            return [], []

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_title(session, url) for url in blog_urls]
            await asyncio.gather(*tasks)

        return self.titles, self.title_hashes

    async def run(self):
        sitemap_links = await self.get_sitemap_urls()
        titles, title_hashes = await self.get_blog_titles(sitemap_links)

        blog_data = {"title_hash": title_hashes, "title": titles}
        self.sitemap_repo.upsert_blog_titles(blog_data=blog_data)

        return {"title_hash": title_hashes, "title": titles}