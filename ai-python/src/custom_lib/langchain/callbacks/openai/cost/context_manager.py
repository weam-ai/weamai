from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalcCallbackHandler
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from src.logger.default_logger import logger

@asynccontextmanager
async def get_custom_openai_callback(model_name: str, cost:str=None, thread_id:str=None, collection_name:str=None,**kwargs) -> AsyncGenerator[CostCalcCallbackHandler, None]:
    """Get the OpenAI callback handler in a context manager which conveniently exposes token and cost information."""
    cb = CostCalcCallbackHandler(model_name=model_name, cost=cost, thread_id=thread_id, collection_name=collection_name,**kwargs)
    try:
        yield cb
    except Exception as e:
        logger.error(
            f"Failed to async context manager: {e}",
            extra={"tags": {"method": "streaming.async_streaming_handler"}}
        )
        raise e
    finally:
        logger.info(
            "Async context manager completed",
            extra={"tags": {"method": "get_custom_openai_callback"}}
        )