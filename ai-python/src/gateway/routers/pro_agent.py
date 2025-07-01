from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.chatflow_langchain.controller.pro_agent_hub import ProAgentController
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
from src.gateway.schema.pro_agent import ProAgentRequestSchema
import os
from src.gateway.custom_fastapi.streaming_response import StreamingResponseWithStatusCode
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import gc

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_stream_chat = os.getenv("LIM_SCRAPE", "5/minute")

@router.post(
    "/pro-agent",
    summary="Scrape Webpage Content",
    description="Endpoint to scrape the content from a specified URL.",
    response_description="Response containing the task chain ID for the scraping operation.",
)
async def pro_agent(
    request: Request,
    agent_request: ProAgentRequestSchema,
    current_user=Depends(get_user_data)
):
    """
    Scrape Webpage Content.

    This endpoint allows users to scrape the content from a specified URL.

    Args:
        request (Request): The incoming HTTP request.
        scrape_request (ProAgentRequestSchema): Input data for the scraping request.
        current_user: The current user making the request.

    Returns:
        dict: A message containing the task chain ID for the scraping operation.

    Raises:
        HTTPException: If there is an error processing the request.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/pro-agent")
    try:
        # Initialize the LLM if needed

        agent_service = ProAgentController()
        agent_service.initialization_service_code(pro_agent_code=agent_request.pro_agent_code)
        agent_response =  await agent_service.service_hub_handler(chat_input=agent_request, current_user=current_user)
        logger.info(
            "Successfully executed Scrape Webpage Content API",
            extra={"tags": {"endpoint": "/pro-agent"}}
        )
        return StreamingResponseWithStatusCode(agent_response, media_type="text/event-stream")

    except HTTPException as he:
        logger.error(
            "HTTP error executing Scrape Webpage Content API",
            extra={
                "tags": {
                    "endpoint": "/pro-agent",
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            "Error executing Scrape Webpage Content API",
            extra={
                "tags": {
                    "endpoint": "/pro-agent",
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Internal server error")
    
    finally:
        gc.collect()