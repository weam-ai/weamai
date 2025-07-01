from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.gateway.schema.custom_gpt import CustomGPTDocChatBase
from src.chatflow_langchain.controller.custom_gpt import CustomGPTController
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
from src.gateway.custom_fastapi.streaming_response import StreamingResponseWithStatusCode
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import gc

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_gpt_doc = os.getenv("LIM_CGPT_DOC", "5/minute")

@router.post(
    "/streaming-custom-gpt-chat-with-doc",
    summary="Streaming Custom GPT Chat with Document Model",
    description="Endpoint to interact with Custom GPT document model for chat purposes.",
    response_description="Response message containing the chat outcome with event stream"
)
# @limiter.limit(limit_gpt_doc)
async def stream_custom_gpt_chat_with_doc(
    request: Request,
    chat_input: CustomGPTDocChatBase,
    current_user=Depends(get_user_data)
):
    """
    Chat with Document Model.

    This endpoint allows users to interact with a document-based custom GPT model for chat purposes. It initializes the model with the specified custom GPT ID and model details, handles the chat interaction, and streams the responses back to the client.

    Args:
        request (Request): The incoming HTTP request.
        chat_input (CustomGPTDocChatBase): Input data for the chat session, including custom GPT ID, model details, and chat session ID.
        current_user: The current authenticated user.

    Returns:
        StreamingResponseWithStatusCode: A stream of messages containing the chat outcome, sent with the "text/event-stream" media type.

    Raises:
        HTTPException: If there is an error processing or storing the text, such as issues with the input data or server errors.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/streaming-custom-gpt-chat-with-doc")
    try:
        custom_gpt_controller=CustomGPTController()
        chat_input.extra_file_ids = chat_input.file_id
        chat_input.extra_tags = chat_input.tag
        custom_gpt_controller.initialization_custom_gpt_code(code=chat_input.code)
        response_generator = await custom_gpt_controller.custom_gpt_hub_handler(chat_input)
        
        logger.info(
            "Successfully executed Chat With Document Model API",
            extra={"tags": {"endpoint": "/streaming-custom-gpt-chat-with-doc", "chat_session_id": chat_input.chat_session_id}}
        )
        
        return StreamingResponseWithStatusCode(response_generator, media_type="text/event-stream")
     
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={
                "tags": {
                    "endpoint": "/streaming-custom-gpt-chat-with-doc",
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
                    "endpoint": "/streaming-custom-gpt-chat-with-doc",
                    "chat_session_id": chat_input.chat_session_id,
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    finally:
        gc.collect()


@router.post(
    "/mock-streaming-custom-gpt-chat-with-doc",
    summary="Streaming Custom GPT Chat with Document Model",
    description="Endpoint to interact with Custom GPT document model for chat purposes.",
    response_description="Response message containing the chat outcome with event stream"
)
# @limiter.limit(limit_gpt_doc)
async def stream_custom_gpt_chat_with_doc(
    request: Request,
    chat_input: CustomGPTDocChatBase,
    current_user=Depends(get_user_data)
):
    """
    Chat with Document Model.

    This endpoint allows users to interact with a document-based custom GPT model for chat purposes. It initializes the model with the specified custom GPT ID and model details, handles the chat interaction, and streams the responses back to the client.

    Args:
        request (Request): The incoming HTTP request.
        chat_input (CustomGPTDocChatBase): Input data for the chat session, including custom GPT ID, model details, and chat session ID.
        current_user: The current authenticated user.

    Returns:
        StreamingResponseWithStatusCode: A stream of messages containing the chat outcome, sent with the "text/event-stream" media type.

    Raises:
        HTTPException: If there is an error processing or storing the text, such as issues with the input data or server errors.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/mock-streaming-custom-gpt-chat-with-doc")
    try:
        custom_gpt_manager=CustomGPTController()
        custom_gpt_manager.Initilization_custom_gpt(
            custom_gpt_id=chat_input.custom_gpt_id,
            customgptmodel=chat_input.customgptmodel
        )
        response_generator = await custom_gpt_manager.custom_gpt_chat_handler(chat_input)
        
        logger.info(
            "Successfully executed Chat With Document Model API",
            extra={"tags": {"endpoint": "/mock-streaming-custom-gpt-chat-with-doc", "chat_session_id": chat_input.chat_session_id}}
        )
        
        return StreamingResponseWithStatusCode(response_generator, media_type="text/event-stream")
     
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={
                "tags": {
                    "endpoint": "/mock-streaming-custom-gpt-chat-with-doc",
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
                    "endpoint": "/mock-streaming-custom-gpt-chat-with-doc",
                    "chat_session_id": chat_input.chat_session_id,
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
