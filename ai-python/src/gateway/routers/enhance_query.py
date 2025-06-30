from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.gateway.schema.enhancement import EnhanceBase
from src.chatflow_langchain.controller.enhancer_hub import EnhanceController
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import gc

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_title = os.getenv("LIM_TITLE", "5/minute")

@router.post(
    "/enhance-query-generate",
    summary="enhance query generation api ",
    description="Endpoint to generate enhance query ",
    response_description="enhance the user query",
   
)
# @limiter.limit(limit_title)
async def enhance_query_generate(
    request: Request,
    chat_input: EnhanceBase,
    current_user=Depends(get_user_data)
):
    """
    Chat with Document Model.

    This endpoint allows users to interact with the document model for chat purposes.

    Args:
        request (Request): The incoming HTTP request.
        chat_id (str): Unique identifier for the chat session.
        chat_input (ChatBase): Input data for the chat session.

    Returns:
        str: A message containing the chat outcome.

    Raises:
        HTTPException: If there is an error processing or storing the text.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/enhance-query-generate")
    try:
        enhance_service = EnhanceController()
        enhance_service.initialization_service_code(code=chat_input.code)
        ehnace_response = await enhance_service.service_hub_handler(chat_input=chat_input,current_user=current_user)
        return ehnace_response
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={"tags": {"endpoint": "/enhance-query-generate", "query_id": chat_input.query_id, "error": str(he)}})
        raise he
    except Exception as e:
        logger.error(
            f"Failed to generate title and store text due to: {e}",
            extra={"tags": {"endpoint": "/enhance-query-generate", "query_id": chat_input.query_id}})
        raise HTTPException(        
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to generate title and store text")
   
    finally:
        gc.collect()