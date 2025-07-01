from src.custom_lib.langchain.callbacks.gemini.cost.cost_calc_handler import GeminiTokenUsageCallbackAsync,GeminiTokenUsageCallbackSync
from typing import Generator,AsyncGenerator
from contextlib import contextmanager,asynccontextmanager
from contextvars import ContextVar
from typing import Optional
from langchain_core.tracers.context import register_configure_hook
from typing import Generator,AsyncGenerator
from contextlib import contextmanager,asynccontextmanager
from contextvars import ContextVar
from typing import Optional
from langchain_core.tracers.context import register_configure_hook
gemini_callback_var: ContextVar[Optional[GeminiTokenUsageCallbackAsync]] = ContextVar(
    "gemini_callback", default=None
)
register_configure_hook(gemini_callback_var, True)


@asynccontextmanager
async def gemini_async_cost_handler(model_name:str, thread_id:str, collection_name:str,*args, **kwargs)-> AsyncGenerator[GeminiTokenUsageCallbackAsync, None]:
    handler = GeminiTokenUsageCallbackAsync(model_name, thread_id, collection_name,*args, **kwargs)
    try:
        yield handler
    except Exception as e:
    
        raise e      
    
@contextmanager
def gemini_sync_cost_handler(model_name:str) -> Generator[GeminiTokenUsageCallbackSync, None, None]:
    """Get the OpenAI callback handler in a context manager.
    which conveniently exposes token and cost information.

    Returns:
        OpenAICallbackHandler: The OpenAI callback handler.

    Example:
        >>> with anthropic_callback() as cb:
        ...     # Use the OpenAI callback handler
    """ 
    cb = GeminiTokenUsageCallbackSync(model_name=model_name)
    gemini_callback_var.set(cb)
    yield cb
    gemini_callback_var.set(None)