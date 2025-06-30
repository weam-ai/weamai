import asyncio
import logging
from fastapi import FastAPI
from typing import Optional, Dict, Any

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AsyncLogger:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def log(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None):
        """Asynchronously log a message with optional extra context."""
        loop = asyncio.get_running_loop()
        if extra:
            await loop.run_in_executor(None, self.logger.log, level, message, extra)
        else:
            await loop.run_in_executor(None, self.logger.log, level, message)

    async def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        await self.log(logging.INFO, message, extra)

    async def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        await self.log(logging.WARNING, message, extra)

    async def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        await self.log(logging.ERROR, message, extra)

    async def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        await self.log(logging.DEBUG, message, extra)

    async def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        await self.log(logging.CRITICAL, message, extra)

async_logger = AsyncLogger(logger)

# async def log_request(request: Request, call_next: Callable):
#     """Middleware to log requests and responses."""
#     start_time = time.time()
#     await async_logger.info(f"Request: {request.method} {request.url}")

#     response: Response = await call_next(request)

#     process_time = time.time() - start_time
#     await async_logger.info(f"Response: {response.status_code} - Process Time: {process_time:.4f}s")
#     return response

# app.middleware("http")(log_request)

# @app.get("/")
# async def read_root():
#     await async_logger.info("Root endpoint accessed")
#     return {"Hello": "World"}

# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Optional[str] = None):
#     await async_logger.info(f"Item ID: {item_id}, Query: {q}")
#     if item_id == 0:
#         await async_logger.error("Item ID 0 is invalid")
#         return JSONResponse(status_code=400, content={"message": "Invalid item ID"})
#     return {"item_id": item_id, "q": q}

# async def background_task(message: str):
#     await async_logger.info(f"Background task started: {message}")
#     await asyncio.sleep(2)
#     await async_logger.info(f"Background task finished: {message}")

# @app.post("/background_task/{message}")
# async def trigger_background_task(message: str):
#     asyncio.create_task(background_task(message))
#     return {"message": "Background task triggered"}