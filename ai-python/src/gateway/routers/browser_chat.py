from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.gateway.schema.browser import BrowserChatBase
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
from src.gateway.custom_fastapi.streaming_response import StreamingResponseWithStatusCode
from src.chatflow_langchain.controller.browser import BrowserController
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import gc

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_tool_chat = os.getenv("LIM_TOOL_CHAT", "5/minute")

@router.post(
    "/stream-browser-chat",
    summary="Stream Browser Chat",
    description="Endpoint to interact with the Perplexity model for chat purposes.",
    response_description="Response message containing the chat outcome.",
)
# @limiter.limit(limit_tool_chat)
async def browser_chat(
    request: Request,
    chat_input: BrowserChatBase,
    current_user=Depends(get_user_data)
):
    """
    Tool Chat with OpenAI Model.

    This endpoint allows users to interact with the OpenAI model for chat purposes.

    Args:
        request (Request): The incoming HTTP request.
        chat_id (str): Unique identifier for the chat session.
        chat_input (ToolChatBase): Input data for the chat session.

    Returns:
        str: A message containing the chat outcome.

    Raises:
        HTTPException: If there is an error processing or storing the text.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/stream-browser-chat")
    try:
        query = chat_input.query
        tool_chat_service=BrowserController()
        tool_chat_service.initialization_service_code(code=chat_input.code)
        response_generator = await tool_chat_service.service_hub_handler(chat_input=chat_input)
        logger.info(
            "Successfully executed Tool chat with Model API",
            extra={"tags": {"endpoint": "/stream-browser-chat", "chat_session_id": chat_input.chat_session_id}}
        )
        return StreamingResponseWithStatusCode(response_generator, media_type="text/event-stream")

    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={
                "tags": {
                    "endpoint": "/stream-browser-chat",
                    "chat_session_id": chat_input.chat_session_id,
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            "Error executing Chat With Document Model API",
            extra={
                "tags": {
                    "endpoint": "/stream-browser-chat",
                    "chat_session_id": chat_input.chat_session_id,
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 
    finally:
        gc.collect()
