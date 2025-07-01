import requests
from fastapi import HTTPException, status
from src.celery_worker_hub.web_scraper.celery_app import celery_app
from src.celery_worker_hub.web_scraper.utils.url_scraper import web_scraping
from src.logger.default_logger import logger

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 0},
    queue="scrapsite"
)
def scrape_website(url: str, notification_data: dict) -> str:
    try:
        web_content = web_scraping(url,notification_data)
        logger.info("Web scraping completed for URL: %s", url)
        return web_content
        
    except requests.RequestException as e:
        logger.error("Request failed for URL %s: %s", url, e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request failed: {e}")
    except Exception as e:
        logger.error("An exception occurred for URL %s: %s", url, e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An exception occurred: {e}")


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 0},
    queue="scrapsite"
)
def scrape_websites_from_dict(url_dict: dict, notification_data: dict) -> dict:
    try:
        results = {}
        for key, url in url_dict.items():
            web_content=web_scraping(url,notification_data)
            results[key] = web_content        
        return results
        
    except requests.RequestException as e:
        logger.error("Request failed for URL %s: %s", url, e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request failed: {e}")
    except Exception as e:
        logger.error("An exception occurred for URL %s: %s", url, e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An exception occurred: {e}")
    

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 0},
    queue="scrapsite"
)
def scrape_list_of_websites(self,url_dict: dict, notification_data: dict) -> dict:
    try:
        results = {}
        for key,list_websites  in url_dict.items():
            list_of_content=[]

            web_dict={}

            for web in list_websites:
                web_content=web_scraping(web,notification_data)
                list_of_content.append(web_content) 
                web_dict[web]=web_content
            results[key]=web_dict
        
        return results
        
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}", extra={"tags": {"method": "ScrapUrlService.scrape_list_of_websites"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An exception occurred: {e}", extra={"tags": {"method": "ScrapUrlService.scrape_list_of_websites"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An exception occurred: {e}")