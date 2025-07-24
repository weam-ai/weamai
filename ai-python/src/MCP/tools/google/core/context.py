# core/context.py
import contextvars
from typing import Optional

# Context variable to hold injected credentials for the life of a single request.
_injected_oauth_credentials = contextvars.ContextVar(
    "injected_oauth_credentials", default=None
)

def get_injected_oauth_credentials():
    """
    Retrieve injected OAuth credentials for the current request context.
    This is called by the authentication layer to check for request-scoped credentials.
    """
    return _injected_oauth_credentials.get()

def set_injected_oauth_credentials(credentials: Optional[dict]):
    """
    Set or clear the injected OAuth credentials for the current request context.
    This is called by the service decorator.
    """
    _injected_oauth_credentials.set(credentials)