from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.gateway.schema.canvas import CanvasBase
from src.chatflow_langchain.controller.canvas import CanvasController
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
limit_canvas = os.getenv("LIM_TITLE", "5/minute")

@router.post(
    "/canvas-chat-generate",
    summary="canvas chat generation api ",
    description="Endpoint to generate canvas chat response",
    response_description="Response message containing the chat outcome.",
   
)
# @limiter.limit(limit_title)
async def canvas_chat_generate(
    request: Request,
    canvas_input: CanvasBase,
    current_user=Depends(get_user_data)
):
    # Log that the API endpoint is called using the helper function
    log_api_call("/canvas-chat-generate")
    try:
        canvas_service = CanvasController()
        canvas_service.initialization_service_code(code=canvas_input.code)
        
        try:

            response_generator = await canvas_service.service_hub_handler(canvas_input)

                
            return StreamingResponseWithStatusCode(response_generator, media_type="text/event-stream")
        except StopAsyncIteration: 
            print("Generator exhausted")
    except HTTPException as he:
        logger.error(
            "HTTP error executing Chat With Document Model API",
            extra={
                "tags": {
                    "endpoint": "/canvas-chat-generate",
                    "chat_session_id": canvas_input.chat_session_id,
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI
    except Exception as e:
        logger.error(
            f"Failed to generate canvas response and store text due to: {e}",
            extra={"tags": {"endpoint": "/canvas-chat-generate", "thread_id": canvas_input.old_thread_id}}
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
    
    finally:
        gc.collect()