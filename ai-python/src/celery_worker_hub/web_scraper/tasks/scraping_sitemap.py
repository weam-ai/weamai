import asyncio
from src.celery_worker_hub.web_scraper.celery_app import celery_app
from src.chatflow_langchain.service.pro_agent.seo_optimizer.sitemap_crawler import SitemapTitleScraper
from src.chatflow_langchain.utils.crawler4ai_scrapper import CrawlerService
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="scrapsite"
)
def scrape_sitemap_task(self, data: dict):
    """Celery Task: Run async scraping in a synchronous Celery worker"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Move scraper init inside loop
    async def run_scraper():
        scraper = SitemapTitleScraper(data=data)
        return await scraper.run()

    result = loop.run_until_complete(run_scraper())
    return result



@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="scrapsite"
)
def crawler_scraper_task(self, urls: list):
    """Celery Task: Run async scraping in a synchronous Celery worker"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Move scraper init inside loop
    async def run_scraper():
        crawler = CrawlerService()
        web_content=await crawler.multiple_crawl_and_clean(urls=urls)
        return web_content

    result = loop.run_until_complete(run_scraper())
    return result

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="scrapsite"
)
def crawler_scraper_task_qa(self, url: str):
    """Celery Task: Run async scraping in a synchronous Celery worker"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Move scraper init inside loop
    async def run_scraper():
        crawler = CrawlerService()
        web_content=await crawler.crawl_and_clean_qa_agent(url=url)
        return web_content

    result = loop.run_until_complete(run_scraper())
    return result

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="scrapsite"
)
def crawler_scraper_task_sales(self, url: str):
    """Celery Task: Run async scraping in a synchronous Celery worker"""

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Move scraper init inside loop
    async def run_scraper():
        crawler = CrawlerService()
        web_content=await crawler.crawl_and_clean(url=url)
        return web_content

    result = loop.run_until_complete(run_scraper())
    return result