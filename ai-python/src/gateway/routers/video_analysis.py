from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.chatflow_langchain.service.pro_agent.video_analysis.upload_file import UploadFileService
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
from src.gateway.schema.pro_agent import ProVideoAnalysisRequestSchema
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
from src.chatflow_langchain.utils.url_validator import URLCheckerService
import gc

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_stream_chat = os.getenv("LIM_SCRAPE", "5/minute")
@router.post(
    "/pro-agent/video/upload-gemini-file",
    summary="Generate a business summary and identify the target audience",
    description=(
        "Processes an uploaded file related to Pro Agent services to generate a comprehensive "
        "business summary and determine the ideal target audience. This endpoint initiates a task "
        "chain for asynchronous processing of the input data."
    ),
    response_description="Response containing the task chain ID for the operation.",
)
async def upload_file_service(
    request: Request,
    agent_request: ProVideoAnalysisRequestSchema,
    current_user=Depends(get_user_data)
):
    """
    Pro Agent Service.

    This endpoint allows users to interact with the Pro Agent service to generate a business summary and identify the target audience.

    Args:
        request (Request): The incoming HTTP request.
        agent_request (ProAgentRequestSchema): Input data for the Pro Agent request.
        current_user: The current user making the request.

    Returns:
        dict: A message containing the task chain ID for the operation.

    Raises:
        HTTPException: If there is an error processing the request.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/video/upload-gemini-file")
    try:
        # Initialize the LLM if needed

          # Initialize the LLM if needed

        upload_service = UploadFileService()
        await upload_service.initialize_chat_input(chat_input=agent_request)
        response=await upload_service.upload_file()

        logger.info(
            "Successfully executed Scrape Webpage Content API",
            extra={"tags": {"endpoint": "/pro-agent"}}
        )
    
        return response

    except HTTPException as he:
        logger.error(
            "HTTP error executing Scrape Webpage Content API",
            extra={
                "tags": {
                    "endpoint": "/video/upload-gemini-file",
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
                    "endpoint": "/video/upload-gemini-file",
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to Upload Gemini")
    
    finally:
        gc.collect()
