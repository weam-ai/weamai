import logging
import os
from typing import Optional
from importlib import metadata

from fastapi import Header
from fastapi.responses import HTMLResponse


from mcp.server.fastmcp import FastMCP
from starlette.requests import Request

from auth.google_auth import start_auth_flow, check_client_secrets
from auth.oauth_callback_server import get_oauth_redirect_uri, ensure_oauth_callback_available
from auth.oauth_responses import create_error_response, create_success_response, create_server_error_response

# Import shared configuration
from auth.scopes import (
    OAUTH_STATE_TO_SESSION_ID_MAP,
    SCOPES,
    USERINFO_EMAIL_SCOPE,  # noqa: F401
    OPENID_SCOPE,  # noqa: F401
    CALENDAR_READONLY_SCOPE,  # noqa: F401
    CALENDAR_EVENTS_SCOPE,  # noqa: F401
    DRIVE_READONLY_SCOPE,  # noqa: F401
    DRIVE_FILE_SCOPE,  # noqa: F401
    GMAIL_READONLY_SCOPE,  # noqa: F401
    GMAIL_SEND_SCOPE,  # noqa: F401
    GMAIL_COMPOSE_SCOPE,  # noqa: F401
    GMAIL_MODIFY_SCOPE,  # noqa: F401
    GMAIL_LABELS_SCOPE,  # noqa: F401
    BASE_SCOPES,  # noqa: F401
    CALENDAR_SCOPES,  # noqa: F401
    DRIVE_SCOPES,  # noqa: F401
    GMAIL_SCOPES,  # noqa: F401
    DOCS_READONLY_SCOPE,  # noqa: F401
    DOCS_WRITE_SCOPE,  # noqa: F401
    CHAT_READONLY_SCOPE,  # noqa: F401
    CHAT_WRITE_SCOPE,  # noqa: F401
    CHAT_SPACES_SCOPE,  # noqa: F401
    CHAT_SCOPES,  # noqa: F401
    SHEETS_READONLY_SCOPE,  # noqa: F401
    SHEETS_WRITE_SCOPE,  # noqa: F401
    SHEETS_SCOPES,  # noqa: F401
    FORMS_BODY_SCOPE,  # noqa: F401
    FORMS_BODY_READONLY_SCOPE,  # noqa: F401
    FORMS_RESPONSES_READONLY_SCOPE,  # noqa: F401
    FORMS_SCOPES,  # noqa: F401
    SLIDES_SCOPE,  # noqa: F401
    SLIDES_READONLY_SCOPE,  # noqa: F401
    SLIDES_SCOPES,  # noqa: F401
    TASKS_SCOPE,  # noqa: F401
    TASKS_READONLY_SCOPE,  # noqa: F401
    TASKS_SCOPES,  # noqa: F401
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WORKSPACE_MCP_PORT = int(os.getenv("PORT", os.getenv("WORKSPACE_MCP_PORT", 8000)))
WORKSPACE_MCP_BASE_URI = os.getenv("WORKSPACE_MCP_BASE_URI", "http://localhost")
USER_GOOGLE_EMAIL = os.getenv("USER_GOOGLE_EMAIL", None)

# Transport mode detection (will be set by main.py)
_current_transport_mode = "stdio"  # Default to stdio

# Basic MCP server instance
server = FastMCP(
    name="google_workspace",
    host = "0.0.0.0",
    port=WORKSPACE_MCP_PORT,
)

def set_transport_mode(mode: str):
    """Set the current transport mode for OAuth callback handling."""
    global _current_transport_mode
    _current_transport_mode = mode
    logger.info(f"Transport mode set to: {mode}")

def get_oauth_redirect_uri_for_current_mode() -> str:
    """Get OAuth redirect URI based on current transport mode."""
    return get_oauth_redirect_uri(WORKSPACE_MCP_PORT, WORKSPACE_MCP_BASE_URI)

# Health check endpoint
@server.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """Health check endpoint for container orchestration."""
    from fastapi.responses import JSONResponse
    try:
        version = metadata.version("workspace-mcp")
    except metadata.PackageNotFoundError:
        version = "dev"
    return JSONResponse({
        "status": "healthy",
        "service": "workspace-mcp",
        "version": version,
        "transport": _current_transport_mode
    })

@server.tool()
async def start_google_auth(
    service_name: str,
    user_google_email: str = USER_GOOGLE_EMAIL,
    mcp_session_id: Optional[str] = Header(None, alias="Mcp-Session-Id")
) -> str:
    """
    Initiates the Google OAuth 2.0 authentication flow for the specified user email and service.
    This is the primary method to establish credentials when no valid session exists or when targeting a specific account for a particular service.
    It generates an authorization URL that the LLM must present to the user.
    The authentication attempt is linked to the current MCP session via `mcp_session_id`.

    LLM Guidance:
    - Use this tool when you need to authenticate a user for a specific Google service (e.g., "Google Calendar", "Google Docs", "Gmail", "Google Drive")
      and don't have existing valid credentials for the session or specified email.
    - You MUST provide the `user_google_email` and the `service_name`. If you don't know the email, ask the user first.
    - Valid `service_name` values typically include "Google Calendar", "Google Docs", "Gmail", "Google Drive".
    - After calling this tool, present the returned authorization URL clearly to the user and instruct them to:
        1. Click the link and complete the sign-in/consent process in their browser.
        2. Note the authenticated email displayed on the success page.
        3. Provide that email back to you (the LLM).
        4. Retry their original request, including the confirmed `user_google_email`.

    Args:
        user_google_email (str): The user's full Google email address (e.g., 'example@gmail.com'). This is REQUIRED.
        service_name (str): The name of the Google service for which authentication is being requested (e.g., "Google Calendar", "Google Docs"). This is REQUIRED.
        mcp_session_id (Optional[str]): The active MCP session ID (automatically injected by FastMCP from the Mcp-Session-Id header). Links the OAuth flow state to the session.

    Returns:
        str: A detailed message for the LLM with the authorization URL and instructions to guide the user through the authentication process.
    """
    if not user_google_email or not isinstance(user_google_email, str) or '@' not in user_google_email:
        error_msg = "Invalid or missing 'user_google_email'. This parameter is required and must be a valid email address. LLM, please ask the user for their Google email address."
        logger.error(f"[start_google_auth] {error_msg}")
        raise Exception(error_msg)

    if not service_name or not isinstance(service_name, str):
        error_msg = "Invalid or missing 'service_name'. This parameter is required (e.g., 'Google Calendar', 'Google Docs'). LLM, please specify the service name."
        logger.error(f"[start_google_auth] {error_msg}")
        raise Exception(error_msg)

    logger.info(f"Tool 'start_google_auth' invoked for user_google_email: '{user_google_email}', service: '{service_name}', session: '{mcp_session_id}'.")

    # Ensure OAuth callback is available for current transport mode
    redirect_uri = get_oauth_redirect_uri_for_current_mode()
    if not ensure_oauth_callback_available(_current_transport_mode, WORKSPACE_MCP_PORT, WORKSPACE_MCP_BASE_URI):
        raise Exception("Failed to start OAuth callback server. Please try again.")

    auth_result = await start_auth_flow(
        mcp_session_id=mcp_session_id,
        user_google_email=user_google_email,
        service_name=service_name,
        redirect_uri=redirect_uri
    )
    return auth_result
