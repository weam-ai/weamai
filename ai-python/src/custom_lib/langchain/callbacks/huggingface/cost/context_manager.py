from src.custom_lib.langchain.callbacks.huggingface.cost.cost_calc_handler import CostCalcCallbackHandler
from src.custom_lib.langchain.callbacks.huggingface.cost.cost_calc_basehandler import HuggingfaceCallbackHandler
from typing import Dict, List, Any, Generator,AsyncGenerator
from contextlib import contextmanager,asynccontextmanager
from src.logger.default_logger import logger
from typing import Optional

@asynccontextmanager
async def get_custom_huggingface_callback(model_name: str, cost:str=None, thread_id:str=None, collection_name:str=None,**kwargs) -> AsyncGenerator[CostCalcCallbackHandler, None]:
    """Get the OpenAI callback handler in a context manager which conveniently exposes token and cost information."""
    cb = CostCalcCallbackHandler(model_name="gpt-4.1-mini", cost=cost, thread_id=thread_id, collection_name=collection_name,**kwargs)
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
        
from contextvars import ContextVar
from langchain_core.tracers.context import register_configure_hook
openai_callback_var: ContextVar[Optional[HuggingfaceCallbackHandler]] = ContextVar(
    "openai_callback", default=None
)
register_configure_hook(openai_callback_var, True)
@contextmanager
def get_huggingface_callback() -> Generator[HuggingfaceCallbackHandler, None, None]:
    """Get the OpenAI callback handler in a context manager.
    which conveniently exposes token and cost information.

    Returns:
        OpenAICallbackHandler: The OpenAI callback handler.

    Example:
        >>> with get_openai_callback() as cb:
        ...     # Use the OpenAI callback handler
    """ 
    cb = HuggingfaceCallbackHandler()
    openai_callback_var.set(cb)
    yield cb
    openai_callback_var.set(None)