from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.chatflow_langchain.controller.scraper import ScrapeController
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
from src.gateway.schema.scrape import ScrapeRequest,ScrapeResponse
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import gc

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_stream_chat = os.getenv("LIM_SCRAPE", "5/minute")

@router.post(
    "/scrape-url",
    summary="Scrape URL",
    description="Endpoint to scrape the content of a given URL.",
    response_description="Response message containing the scraped content.",
)
async def scrape_url(
    request: Request,
    scrape_request: ScrapeRequest,
    current_user=Depends(get_user_data)
):
    """
    Scrape URL.

    This endpoint allows users to scrape the content of a given URL.

    Args:
        request (Request): The incoming HTTP request.
        scrape_request (ScrapeRequest): Input data for the scraping request.
        current_user: The current user making the request.

    Returns:
        ScrapeResponse: A message containing the scraped content.

    Raises:
        HTTPException: If there is an error processing the request.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/scrape-url")
    try:
        # Initialize the LLM if needed
        scrap_url_service = ScrapeController()
        scrap_url_service.initialization_service_code(code=scrape_request.code)
        scrape_response = await scrap_url_service.service_hub_handler(chat_input=scrape_request,current_user=current_user)
        logger.info(
            "Successfully executed Scrape URL API",
            extra={"tags": {"endpoint": "/scrape-url"}}
        )
        return ScrapeResponse(task_chain_id=scrape_response)

    except HTTPException as he:
        logger.error(
            "HTTP error executing Scrape URL API",
            extra={
                "tags": {
                    "endpoint": "/scrape-url",
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            "Error executing Scrape URL API",
            extra={
                "tags": {
                    "endpoint": "/scrape-url",
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    finally:
        gc.collect()