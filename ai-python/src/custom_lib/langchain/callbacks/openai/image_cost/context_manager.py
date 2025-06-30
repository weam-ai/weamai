from typing import AsyncGenerator
from src.custom_lib.langchain.callbacks.openai.image_cost.dalle_cost import DalleCostcallback
from contextlib import asynccontextmanager
from src.logger.default_logger import logger
import gc

@asynccontextmanager
async def dalle_callback_handler(llm_model,dalle_model,cost=None,thread_id:str=None, collection_name:str=None,**kwargs) -> AsyncGenerator[DalleCostcallback, None]:
    """Get the OpenAI callback handler in a context manager which conveniently exposes token and cost information."""
    cb = DalleCostcallback(llm_model,dalle_model,cost,thread_id, collection_name,**kwargs)
    try:
        yield cb
    except Exception as e:
        logger.error(
            f"Failed to async context manager: {e}",
            extra={"tags": {"method": "streaming.async_streaming_handler"}})
        raise e
    finally:
        gc.collect()
        # Clean up or finalize if necessary
        logger.info("==DalleCostcallback==") 