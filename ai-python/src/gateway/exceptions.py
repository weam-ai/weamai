from fastapi import FastAPI
from starlette.responses import JSONResponse
from fastapi import FastAPI,Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from src.logger.default_logger import logger
import pymongo
from src.gateway.utils import map_error, handle_initialization
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG,HF_ERROR_MESSAGES_CONFIG,ANTHROPIC_ERROR_MESSAGES_CONFIG,GENAI_ERROR_MESSAGES_CONFIG
from src.chatflow_langchain.service.openai.title.title_generator import OpenAITitleGenerationService
from src.chatflow_langchain.service.openai.title.utils import get_default_title

# FastAPI app instance
ERROR_PLATFORM={"ANTHROPIC":ANTHROPIC_ERROR_MESSAGES_CONFIG,"HUGGING_FACE":HF_ERROR_MESSAGES_CONFIG,"OPEN_AI":OPENAI_MESSAGES_CONFIG,"GEMINI":GENAI_ERROR_MESSAGES_CONFIG}
app = FastAPI()

title_service = OpenAITitleGenerationService()
class CustomTitleHttpException(HTTPException):
    def __init__(self, status_code: int, detail: str, data: dict = None):
        super().__init__(status_code=status_code, detail=detail)
        self.data = data if data else {}

class ChatPerplexityException(Exception):
    """Custom exception for ChatPerplexity-related errors."""
    def __init__(self, message, error_code=None):
        super().__init__(message)
        self.error_code = error_code

class PayloadTooLargeException(HTTPException):
    def __init__(self, status_code: int,detail: str = "Request payload too large"):
        super().__init__(status_code=status_code, detail=detail)

class AudioTooLargeException(HTTPException):
    def __init__(self, status_code: int, detail: str = "Audio too large"):
        super().__init__(status_code=status_code, detail=detail)
# Handler for CustomTitleHttpException
@app.exception_handler(CustomTitleHttpException)
async def custom_title_http_exception_handler(request: Request, exc: CustomTitleHttpException):
    chat_session_id = exc.data.get("chat_session_id")
    chatmodel = exc.data.get("chatmodel")
    chatmembermodel = exc.data.get("chatmembermodel")

    default_title = get_default_title("default")

    # Ensure that the title updates are performed
    try:
        title_service.update_chat_session_title(chat_session_id, default_title, collection_name=chatmodel)
        title_service.update_chat_member_title(chat_session_id, default_title, collection_name=chatmembermodel)
    except Exception as update_error:
        logger.error(f"Failed to update titles for session {chat_session_id}: {update_error}")

    logger.error(f"CustomTitleHttpException occurred: {exc.detail}, Title: {default_title}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": exc.status_code,
            "message": exc.detail,
            "title": default_title})



# Custom handler for RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    try:
        payload = await request.json()
        handle_initialization(payload)
    except Exception as e:
        logger.error(f"Failed to extract payload in validation handler: {e}")

    errors = exc.errors()

    response = OPENAI_MESSAGES_CONFIG.get("common_response")
    if errors:
        for error in errors:
            loc = error.get("loc", [])
            field = loc[-1] if loc else "unknown"
            location = " -> ".join(str(x) for x in loc)
            msg = error.get("msg", "Unknown validation error")
            input_value = error.get("input", None)
            logger.error(f"❌ '{field}' in {location} is invalid: {msg}. Received type: {type(input_value).__name__}")

        first_error = errors[0]
        error_type = first_error["type"]
        field_name = str(first_error.get("loc")[-1])  # Convert field_name to string

        message = map_error(error_type, field_name)

        logger.error(f"Validation error: {message}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": DEV_MESSAGES_CONFIG.get("dev_message"),
                "data": response
            }
        )

    default_message = "Invalid JSON format"
    logger.error(f"Validation error: {default_message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": DEV_MESSAGES_CONFIG.get("dev_message"),
            "data": response
        }
    )

@app.exception_handler(PayloadTooLargeException)
async def payload_too_large_handler(request: Request, exc: PayloadTooLargeException):
    logger.error(f"Payload too large: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content={
            "status": 413,
            "message": "The uploaded content exceeds the allowed limit. Video length should not exceed 30 minutes",
            "data": {}
        }
    )

@app.exception_handler(AudioTooLargeException)
async def audio_too_large_handler(request: Request, exc: AudioTooLargeException):
    logger.error(f"Content Too Large: {exc.detail}")
    response = GENAI_ERROR_MESSAGES_CONFIG.get("audio_length_exceeded")
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content={
            "status": 413,
            "message": "Audio length exceeds the limit of 1 hour 30 minutes.",
            "data": response
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):

    
    try:
        platforms_to_check = ["HUGGING_FACE", "ANTHROPIC", "GEMINI"]        
        if not (isinstance(exc.detail,dict) and exc.detail.get('platform') in platforms_to_check):                      
            payload = await request.json()
            handle_initialization(payload)
    except Exception as e:
        logger.error(f"Failed to extract payload in HTTP handler: {e}")
    logger.error(f"HTTP {exc.status_code} Error occurred: {exc.detail}")

    if isinstance(exc.detail,str):
        response = OPENAI_MESSAGES_CONFIG.get("common_response")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status":exc.status_code,
                "message": DEV_MESSAGES_CONFIG.get("dev_message"),
                "data": response
                }
            )
    elif isinstance(exc.detail,dict):
        platform_code=exc.detail['platform']
        message=exc.detail['message']
        error_code=exc.detail['error_code']
        
        response = ERROR_PLATFORM[platform_code].get(error_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status":exc.status_code,
                "message": message,
                "data": response
                }
            )
    else:
        response = OPENAI_MESSAGES_CONFIG.get("common_response")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status":exc.status_code,
                "message": DEV_MESSAGES_CONFIG.get("dev_message"),
                "data": response
                }
            )

@app.exception_handler(pymongo.errors.ServerSelectionTimeoutError)
async def mongodb_connection_error_handler(request: Request, exc: pymongo.errors.ServerSelectionTimeoutError):
    return JSONResponse(
        status_code=500,
        content={"message": "Failed to connect to MongoDB. Please try again later."}
    )

@app.exception_handler(400)
async def bad_request_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": status.HTTP_400_BAD_REQUEST,
            "message": exc.detail,
            "data": {},
        },
    )

@app.exception_handler(401)
async def internal_server_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "status": status.HTTP_401_UNAUTHORIZED,
            "message": exc.detail,
            "data": {}}
    )

@app.exception_handler(404)
async def not_found_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "status": status.HTTP_404_NOT_FOUND,
            "message": exc.detail,
            "data": {},
        },
    )

@app.exception_handler(422)
async def unprocessable_entity_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": exc.detail,
            "data": {},
        },
    )

@app.exception_handler(429)
async def too_many_requests_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "status": status.HTTP_429_TOO_MANY_REQUESTS,
            "message": exc.detail,
            "data": {},
        },
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": exc.detail,
            "data": {},
            }
    )



