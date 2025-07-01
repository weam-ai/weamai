from typing import Any, Dict
import tiktoken as tiktoken_

# Global cache for encoding objects.
global_encoding_cache: Dict[str, Any] = {}

def get_cached_encoding(model: str) -> Any:
    """Return a cached encoding for the given model, or initialize and cache it if needed."""
    if model in global_encoding_cache:
        return global_encoding_cache[model]
    try:
        encoding = tiktoken_.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken_.get_encoding("cl100k_base")
    global_encoding_cache[model] = encoding
    return encoding