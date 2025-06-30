from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.gateway.schema.image import ImageBase
from src.chatflow_langchain.service.openai.image.image_generation import OpenAIImageGenerationService
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
limit_generate_image = os.getenv("LIM_IMG_GEN", "5/minute")

@router.post(
    "/generate-image",
    summary="Generate Image from Dalle",
    description="Endpoint to generate image with the Dalle model.",
    response_description="Response message containing image.",
)
# @limiter.limit(limit_generate_image)
async def image_generation(
    request: Request,
    chat_input: ImageBase,
    current_user=Depends(get_user_data)
):
    """
    Image Generation.

    This endpoint allows users to generate image with the Dalle model.

    Args:
        request (Request): The incoming HTTP request.
        chat_id (str): Unique identifier for the chat session.
        chat_input (ChatBase): Input data for the chat session.

    Returns:
        str: A message containing url of image generated.

    Raises:
        HTTPException: If there is an error processing or storing the text.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/generate-image")
    try:
        image_service = OpenAIImageGenerationService()
        image_service.initialize_llm_tool(
            api_key_id=chat_input.llm_apikey,
            companymodel=chat_input.companymodel,
            dalle_wrapper_size = chat_input.dalle_wrapper_size,
            dalle_wrapper_quality = chat_input.dalle_wrapper_quality,
            dalle_wrapper_style = chat_input.dalle_wrapper_style,
        )
        image_service.initialize_repository(
            chat_session_id=chat_input.chat_session_id,
            collection_name=chat_input.threadmodel
        )

        # prompt attach
        image_service.prompt_attach(additional_prompt_id=chat_input.prompt_id,collection_name=chat_input.promptmodel)  

        ## conversation create 
        image_service.create_conversation(input_text=chat_input.query)  

        # streaming the chat chat serivce
        response_generator = image_service.run_image_generation(thread_id=chat_input.thread_id, \
                                                                         collection_name=chat_input.threadmodel,delay_chunk=chat_input.delay_chunk)
        logger.info(
            "Successfully executed Image generation Model API",
            extra={"tags": {"endpoint": "/generate-image", "chat_session_id": chat_input.chat_session_id}}
        )
        return StreamingResponseWithStatusCode(response_generator, media_type="application/json")

    except HTTPException as he:
        logger.error(
            "HTTP error executing Image generation Model API",
            extra={
                "tags": {
                    "endpoint": "/generate-image",
                    "chat_session_id": chat_input.chat_session_id,
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            "Error executing Image generation Model API",
            extra={
                "tags": {
                    "endpoint": "/generate-image",
                    "chat_session_id": chat_input.chat_session_id,
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error") 

    finally:
        gc.collect()