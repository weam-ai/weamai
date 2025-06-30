from src.custom_lib.langchain.callbacks.weam_router.open_router.cost.cost_calc_handler import OpenRouterTokenUsageCallbackSync,OpenRouterTokenUsageCallbackAsync
from typing import Generator,AsyncGenerator, Optional
from contextlib import contextmanager,asynccontextmanager
from src.logger.default_logger import logger
from contextvars import ContextVar
from langchain_core.tracers.context import register_configure_hook
openrouter_callback_var: ContextVar[Optional[OpenRouterTokenUsageCallbackSync]] = ContextVar(
    "openrouter_callback", default=None
)
register_configure_hook(openrouter_callback_var, True)
@asynccontextmanager
async def openrouter_async_callback(model_name: str, thread_id:str=None, collection_name:str=None,**kwargs) -> AsyncGenerator[OpenRouterTokenUsageCallbackAsync, None]:
    """Get the OpenAI callback handler in a context manager which conveniently exposes token and cost information."""
    cb = OpenRouterTokenUsageCallbackAsync(model_name=model_name, thread_id=thread_id, collection_name=collection_name,**kwargs)
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
def openrouter_sync_callback(model_name:str) -> Generator[OpenRouterTokenUsageCallbackSync, None, None]:
    """Get the OpenAI callback handler in a context manager.
    which conveniently exposes token and cost information.

    Returns:
        OpenAICallbackHandler: The OpenAI callback handler.

    Example:
        >>> with anthropic_callback() as cb:
        ...     # Use the OpenAI callback handler
    """ 
    cb = OpenRouterTokenUsageCallbackSync(model_name=model_name)
    openrouter_callback_var.set(cb)
    yield cb
    openrouter_callback_var.set(None)