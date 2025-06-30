from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from src.gateway.api_router import api_router
from dotenv import load_dotenv
import os

load_dotenv()

enable_swagger = os.getenv("ENABLE_SWAGGER", "false").strip().lower() == "true"
enable_redoc = os.getenv("ENABLE_REDOC", "false").strip().lower() == "true"

app = FastAPI(
    docs_url="/docs" if enable_swagger else None,
    redoc_url="/redoc" if enable_redoc else None
)

# Allow all origins, all methods, and all headers:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(api_router)

Instrumentator().instrument(app).expose(app)

@app.exception_handler(RateLimitExceeded)
async def custom_429_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try after a minute."},
    )
