from src.custom_lib.langchain.callbacks.perplexity.cost.cost_calc_handler import PerplexityTokenUsageCallbackAsync,PerplexityTokenUsageCallbackSync
from typing import Generator,AsyncGenerator
from contextlib import contextmanager,asynccontextmanager
from contextvars import ContextVar
from typing import Optional
from langchain_core.tracers.context import register_configure_hook
from contextlib import contextmanager,asynccontextmanager
from contextvars import ContextVar
from langchain_core.tracers.context import register_configure_hook
perplexity_callback_var: ContextVar[Optional[PerplexityTokenUsageCallbackAsync]] = ContextVar(
    "perplexity_callback", default=None
)
register_configure_hook(perplexity_callback_var, True)


@asynccontextmanager
async def perplexity_async_cost_handler(model_name:str, thread_id:str, collection_name:str,*args, **kwargs)-> AsyncGenerator[PerplexityTokenUsageCallbackAsync, None]:
    handler = PerplexityTokenUsageCallbackAsync(model_name, thread_id, collection_name,*args, **kwargs)
    try:
        yield handler
    except Exception as e:
        raise e      
    
@contextmanager
def perplexity_sync_cost_handler(model_name:str) -> Generator[PerplexityTokenUsageCallbackSync, None, None]:
    """Get the OpenAI callback handler in a context manager.
    which conveniently exposes token and cost information.

    Returns:
        OpenAICallbackHandler: The OpenAI callback handler.

    Example:
        >>> with anthropic_callback() as cb:
        ...     # Use the OpenAI callback handler
    """ 
    cb = PerplexityTokenUsageCallbackSync(model_name=model_name)
    perplexity_callback_var.set(cb)
    yield cb
    perplexity_callback_var.set(None)