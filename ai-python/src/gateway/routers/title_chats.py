from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.gateway.schema.title import TitleBase
from src.chatflow_langchain.controller.title import TitleController
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import gc
from src.gateway.exceptions import CustomTitleHttpException

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_title = os.getenv("LIM_TITLE", "5/minute")


@router.post(
    "/title-chat-generate",
    summary="title chat generation api ",
    description="Endpoint to generate title of chat session",
    response_description="Response message containing the chat outcome.",
   
)
# @limiter.limit(limit_title)
async def title_chat_generate(
    request: Request,
    title_input: TitleBase,
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
    log_api_call("/title-chat-generate")
    try:
        title_service = TitleController()
        title_service.initialization_service_code(code=title_input.code)
        Title = await title_service.service_hub_handler(chat_input=title_input,current_user=current_user)
        return Title
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={"tags": {"endpoint": "/title-chat-generate", "chat_session_id": title_input.chat_session_id, "error": str(he)}})
    
        raise CustomTitleHttpException(
            status_code=he.status_code,
            detail="Title generating was interrupted by an issue.",
            data={"chat_session_id":title_input.chat_session_id,"chatmodel":title_input.chatmodel,"chatmembermodel":title_input.chatmembermodel})

    except Exception as e:
        logger.error(
            f"Failed to generate title and store text due to: {e}",
            extra={"tags": {"endpoint": "/title-chat-generation", "thread_id": title_input.thread_id}})

        raise CustomTitleHttpException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title generating was interrupted by an issue.",
            data={"chat_session_id":title_input.chat_session_id,"chatmodel":title_input.chatmodel,"chatmembermodel":title_input.chatmembermodel})
    finally:
        gc.collect()