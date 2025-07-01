from src.custom_lib.langchain.callbacks.anthropic.cost.cost_calc_handler import AnthropicTokenUsageCallbackAsync,AnthropicTokenUsageCallbackSync
from typing import Dict, List, Any, Generator,AsyncGenerator
from contextlib import contextmanager,asynccontextmanager
from src.logger.default_logger import logger
from contextvars import ContextVar
from typing import Optional
from langchain_core.tracers.context import register_configure_hook
anthropic_callback_var: ContextVar[Optional[AnthropicTokenUsageCallbackSync]] = ContextVar(
    "anthropic_callback", default=None
)
register_configure_hook(anthropic_callback_var, True)
@asynccontextmanager
async def anthropic_async_callback(model_name: str, thread_id:str=None, collection_name:str=None,**kwargs) -> AsyncGenerator[AnthropicTokenUsageCallbackAsync, None]:
    """Get the OpenAI callback handler in a context manager which conveniently exposes token and cost information."""
    cb = AnthropicTokenUsageCallbackAsync(model_name=model_name, thread_id=thread_id, collection_name=collection_name,**kwargs)
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
def anthropic_sync_callback() -> Generator[AnthropicTokenUsageCallbackSync, None, None]:
    """Get the OpenAI callback handler in a context manager.
    which conveniently exposes token and cost information.

    Returns:
        OpenAICallbackHandler: The OpenAI callback handler.

    Example:
        >>> with anthropic_callback() as cb:
        ...     # Use the OpenAI callback handler
    """ 
    cb = AnthropicTokenUsageCallbackSync()
    anthropic_callback_var.set(cb)
    yield cb
    anthropic_callback_var.set(None)