from fastapi import FastAPI, HTTPException
from src.gateway.custom_fastapi.streaming_response import StreamingResponseWithStatusCode
from src.gateway.api_router import api_router
from fastapi.exceptions import RequestValidationError
import pymongo
from src.gateway.exceptions import (validation_exception_handler,http_exception_handler,mongodb_connection_error_handler)
from src.gateway.exceptions import custom_title_http_exception_handler,CustomTitleHttpException
from dotenv import load_dotenv
from src.gateway.utils import RegexCORSMiddleware,get_regex_patterns,get_swagger_redoc_settings
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator
from src.gateway.utils import PyInstrumentMiddleWare,MemoryLeakMiddleware,ForceCleanupMiddleware
import os

load_dotenv()
enable_swagger, enable_redoc = get_swagger_redoc_settings()

app = FastAPI(
    docs_url="/docs" if enable_swagger else None,
    redoc_url="/redoc" if enable_redoc else None
)
app.state.last_profiling_data = {}
# regex_patterns = [r".weam\.ai"]

@app.get("/profile")
def get_profile(request: Request):
    # Return the profiling data stored in the app state
    return request.app.state.last_profiling_data

regex_patterns = get_regex_patterns()

app.add_middleware(RegexCORSMiddleware, regex_patterns=regex_patterns)
# app.add_middleware(APICountMiddleware)
# app.add_middleware(APICountMiddlewareRedis)
# app.add_middleware(MultiAPICountMiddlewareRedis)
app.include_router(api_router)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(pymongo.errors.ServerSelectionTimeoutError, mongodb_connection_error_handler)
app.add_exception_handler(CustomTitleHttpException, custom_title_http_exception_handler)
app.add_middleware(ForceCleanupMiddleware)

local_environment = os.getenv("WEAM_ENVIRONMENT", "local")
if local_environment in ["local", "dev"]:
    app.add_middleware(PyInstrumentMiddleWare)
    # app.add_middleware(MemoryLeakMiddleware)

Instrumentator().instrument(app).expose(app)

import asyncio
async def waypoints_generator():
    # Initial dummy event to ensure the connection is properly established
    words = [
        "Virat", "Kohli", "Indian", "cricketer", "aggressive", 
        "batting", "records", "captain", "fitness", "discipline", 
        "legendary", "admired", "team", "leader", "run-machine",
        "Delhi", "IPL", "Royal", "Challengers", "Bangalore",
        "centuries", "half-centuries", "boundaries", "six", "four",
        "Test", "ODI", "T20", "World", "Cup",
        "Chase", "master", "consistent", "performer", "winning",
        "passion", "determination", "fielding", "catch", "ground",
        "stadium", "fans", "support", "celebration", "trophy",
        "awards", "accolades", "sportsman", "spirit", "mentor",
        "icon", "role", "model", "youngsters", "inspiration",
        "practice", "dedication", "hardwork", "success", "challenge",
        "adversity", "comeback", "fitness", "routine", "training",
        "coach", "strategies", "tactics", "partnership", "runs",
        "innings", "opening", "middle-order", "finisher", "winning",
        "spree", "glory", "hero", "iconic", "brand",
        "endorsements", "celebrity", "lifestyle", "philanthropy", "charity",
        "awareness", "campaign", "social", "media", "presence",
        "followership", "interviews", "speeches", "press", "conferences"
    ]
    
    for words in words:
        # logging.info(f"Yielding word: {words}")
        yield f"data: {words.encode('utf-8')}\n\n",200
        await asyncio.sleep(0.2)

@app.get("/stream")
async def root():
    return StreamingResponseWithStatusCode(waypoints_generator(), media_type="text/event-stream")


@app.get("/ping")
async def ping():
    return {"message": "pong"}

