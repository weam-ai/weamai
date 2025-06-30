from src.custom_lib.langchain.callbacks.weam_router.deep_seek.cost.cost_calc_handler import DeepSeekTokenUsageCallbackSync,DeepSeekTokenUsageCallbackAsync
from typing import Generator,AsyncGenerator, Optional
from contextlib import contextmanager,asynccontextmanager
from src.logger.default_logger import logger
from contextvars import ContextVar
from langchain_core.tracers.context import register_configure_hook
deepseek_callback_var: ContextVar[Optional[DeepSeekTokenUsageCallbackSync]] = ContextVar(
    "deepseek_callback", default=None
)
register_configure_hook(deepseek_callback_var, True)
@asynccontextmanager
async def deepseek_async_callback(model_name: str, thread_id:str=None, collection_name:str=None,**kwargs) -> AsyncGenerator[DeepSeekTokenUsageCallbackAsync, None]:
    """Get the OpenAI callback handler in a context manager which conveniently exposes token and cost information."""
    cb = DeepSeekTokenUsageCallbackAsync(model_name=model_name, thread_id=thread_id, collection_name=collection_name,**kwargs)
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
            extra={"tags": {"method": "anthropic_callback_function"}}
        )




@contextmanager
def deepseek_sync_callback(model_name:str) -> Generator[DeepSeekTokenUsageCallbackSync, None, None]:
    """Get the OpenAI callback handler in a context manager.
    which conveniently exposes token and cost information.

    Returns:
        OpenAICallbackHandler: The OpenAI callback handler.

    Example:
        >>> with anthropic_callback() as cb:
        ...     # Use the OpenAI callback handler
    """ 
    cb = DeepSeekTokenUsageCallbackSync(model_name=model_name)
    deepseek_callback_var.set(cb)
    yield cb
    deepseek_callback_var.set(None)