# auth/google_auth.py

import asyncio
import json
import jwt
import logging
import os

from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from auth.scopes import OAUTH_STATE_TO_SESSION_ID_MAP, SCOPES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory cache for session credentials, maps session_id to Credentials object
# This is brittle and bad, but our options are limited with Claude in present state.
# This should be more robust in a production system once OAuth2.1 is implemented in client.
_SESSION_CREDENTIALS_CACHE: Dict[str, Credentials] = {}
# Centralized Client Secrets Path Logic
_client_secrets_env = os.getenv("GOOGLE_CLIENT_SECRET_PATH") or os.getenv(
    "GOOGLE_CLIENT_SECRETS"
)
if _client_secrets_env:
    CONFIG_CLIENT_SECRETS_PATH = _client_secrets_env
else:
    # Assumes this file is in auth/ and client_secret.json is in the root
    CONFIG_CLIENT_SECRETS_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "client_secret.json",
    )

# --- Helper Functions ---



def save_credentials_to_session(session_id: str, credentials: Credentials):
    """Saves user credentials to the in-memory session cache."""
    _SESSION_CREDENTIALS_CACHE[session_id] = credentials
    logger.debug(f"Credentials saved to session cache for session_id: {session_id}")


def load_credentials_from_session(session_id: str) -> Optional[Credentials]:
    """Loads user credentials from the in-memory session cache."""
    credentials = _SESSION_CREDENTIALS_CACHE.get(session_id)
    if credentials:
        logger.debug(
            f"Credentials loaded from session cache for session_id: {session_id}"
        )
    else:
        logger.debug(
            f"No credentials found in session cache for session_id: {session_id}"
        )
    return credentials


def load_client_secrets_from_env() -> Optional[Dict[str, Any]]:
    """
    Loads the client secrets from environment variables.

    Environment variables used:
        - GOOGLE_OAUTH_CLIENT_ID: OAuth 2.0 client ID
        - GOOGLE_OAUTH_CLIENT_SECRET: OAuth 2.0 client secret
        - GOOGLE_OAUTH_REDIRECT_URI: (optional) OAuth redirect URI

    Returns:
        Client secrets configuration dict compatible with Google OAuth library,
        or None if required environment variables are not set.
    """
    client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_OAUTH_REDIRECT_URI")

    if client_id and client_secret:
        # Create config structure that matches Google client secrets format
        web_config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        }

        # Add redirect_uri if provided via environment variable
        if redirect_uri:
            web_config["redirect_uris"] = [redirect_uri]

        # Return the full config structure expected by Google OAuth library
        config = {"web": web_config}

        logger.info("Loaded OAuth client credentials from environment variables")
        return config

    logger.debug("OAuth client credentials not found in environment variables")
    return None


def load_client_secrets(client_secrets_path: str) -> Dict[str, Any]:
    """
    Loads the client secrets from environment variables (preferred) or from the client secrets file.

    Priority order:
    1. Environment variables (GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET)
    2. File-based credentials at the specified path

    Args:
        client_secrets_path: Path to the client secrets JSON file (used as fallback)

    Returns:
        Client secrets configuration dict

    Raises:
        ValueError: If client secrets file has invalid format
        IOError: If file cannot be read and no environment variables are set
    """
    # First, try to load from environment variables
    env_config = load_client_secrets_from_env()
    if env_config:
        # Extract the "web" config from the environment structure
        return env_config["web"]

    # Fall back to loading from file
    try:
        with open(client_secrets_path, "r") as f:
            client_config = json.load(f)
            # The file usually contains a top-level key like "web" or "installed"
            if "web" in client_config:
                logger.info(
                    f"Loaded OAuth client credentials from file: {client_secrets_path}"
                )
                return client_config["web"]
            elif "installed" in client_config:
                logger.info(
                    f"Loaded OAuth client credentials from file: {client_secrets_path}"
                )
                return client_config["installed"]
            else:
                logger.error(
                    f"Client secrets file {client_secrets_path} has unexpected format."
                )
                raise ValueError("Invalid client secrets file format")
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error loading client secrets file {client_secrets_path}: {e}")
        raise


def check_client_secrets() -> Optional[str]:
    """
    Checks for the presence of OAuth client secrets, either as environment
    variables or as a file.

    Returns:
        An error message string if secrets are not found, otherwise None.
    """
    env_config = load_client_secrets_from_env()
    if not env_config and not os.path.exists(CONFIG_CLIENT_SECRETS_PATH):
        logger.error(
            f"OAuth client credentials not found. No environment variables set and no file at {CONFIG_CLIENT_SECRETS_PATH}"
        )
        return f"OAuth client credentials not found. Please set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET environment variables or provide a client secrets file at {CONFIG_CLIENT_SECRETS_PATH}."
    return None


def create_oauth_flow(
    scopes: List[str], redirect_uri: str, state: Optional[str] = None
) -> Flow:
    """Creates an OAuth flow using environment variables or client secrets file."""
    # Try environment variables first
    env_config = load_client_secrets_from_env()
    if env_config:
        # Use client config directly
        flow = Flow.from_client_config(
            env_config, scopes=scopes, redirect_uri=redirect_uri, state=state
        )
        logger.debug("Created OAuth flow from environment variables")
        return flow

    # Fall back to file-based config
    if not os.path.exists(CONFIG_CLIENT_SECRETS_PATH):
        raise FileNotFoundError(
            f"OAuth client secrets file not found at {CONFIG_CLIENT_SECRETS_PATH} and no environment variables set"
        )

    flow = Flow.from_client_secrets_file(
        CONFIG_CLIENT_SECRETS_PATH,
        scopes=scopes,
        redirect_uri=redirect_uri,
        state=state,
    )
    logger.debug(
        f"Created OAuth flow from client secrets file: {CONFIG_CLIENT_SECRETS_PATH}"
    )
    return flow


# --- Core OAuth Logic ---


async def start_auth_flow(
    mcp_session_id: Optional[str],
    user_google_email: Optional[str],
    service_name: str,  # e.g., "Google Calendar", "Gmail" for user messages
    redirect_uri: str,  # Added redirect_uri as a required parameter
) -> str:
    """
    Initiates the Google OAuth flow and returns an actionable message for the user.

    Args:
        mcp_session_id: The active MCP session ID.
        user_google_email: The user's specified Google email, if provided.
        service_name: The name of the Google service requiring auth (for user messages).
        redirect_uri: The URI Google will redirect to after authorization.

    Returns:
        A formatted string containing guidance for the LLM/user.

    Raises:
        Exception: If the OAuth flow cannot be initiated.
    """
    initial_email_provided = bool(
        user_google_email
        and user_google_email.strip()
        and user_google_email.lower() != "default"
    )
    user_display_name = (
        f"{service_name} for '{user_google_email}'"
        if initial_email_provided
        else service_name
    )

    logger.info(
        f"[start_auth_flow] Initiating auth for {user_display_name} (session: {mcp_session_id}) with global SCOPES."
    )

    try:
        if "OAUTHLIB_INSECURE_TRANSPORT" not in os.environ and (
            "localhost" in redirect_uri or "127.0.0.1" in redirect_uri
        ):  # Use passed redirect_uri
            logger.warning(
                "OAUTHLIB_INSECURE_TRANSPORT not set. Setting it for localhost/local development."
            )
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        oauth_state = os.urandom(16).hex()
        if mcp_session_id:
            OAUTH_STATE_TO_SESSION_ID_MAP[oauth_state] = mcp_session_id
            logger.info(
                f"[start_auth_flow] Stored mcp_session_id '{mcp_session_id}' for oauth_state '{oauth_state}'."
            )

        flow = create_oauth_flow(
            scopes=SCOPES,  # Use global SCOPES
            redirect_uri=redirect_uri,  # Use passed redirect_uri
            state=oauth_state,
        )

        auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
        logger.info(
            f"Auth flow started for {user_display_name}. State: {oauth_state}. Advise user to visit: {auth_url}"
        )

        message_lines = [
            f"**ACTION REQUIRED: Google Authentication Needed for {user_display_name}**\n",
            f"To proceed, the user must authorize this application for {service_name} access using all required permissions.",
            "**LLM, please present this exact authorization URL to the user as a clickable hyperlink:**",
            f"Authorization URL: {auth_url}",
            f"Markdown for hyperlink: [Click here to authorize {service_name} access]({auth_url})\n",
            "**LLM, after presenting the link, instruct the user as follows:**",
            "1. Click the link and complete the authorization in their browser.",
        ]
        session_info_for_llm = (
            f" (this will link to your current session {mcp_session_id})"
            if mcp_session_id
            else ""
        )

        if not initial_email_provided:
            message_lines.extend(
                [
                    f"2. After successful authorization{session_info_for_llm}, the browser page will display the authenticated email address.",
                    "   **LLM: Instruct the user to provide you with this email address.**",
                    "3. Once you have the email, **retry their original command, ensuring you include this `user_google_email`.**",
                ]
            )
        else:
            message_lines.append(
                f"2. After successful authorization{session_info_for_llm}, **retry their original command**."
            )

        message_lines.append(
            f"\nThe application will use the new credentials. If '{user_google_email}' was provided, it must match the authenticated account."
        )
        return "\n".join(message_lines)

    except FileNotFoundError as e:
        error_text = f"OAuth client credentials not found: {e}. Please either:\n1. Set environment variables: GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET\n2. Ensure '{CONFIG_CLIENT_SECRETS_PATH}' file exists"
        logger.error(error_text, exc_info=True)
        raise Exception(error_text)
    except Exception as e:
        error_text = f"Could not initiate authentication for {user_display_name} due to an unexpected error: {str(e)}"
        logger.error(
            f"Failed to start the OAuth flow for {user_display_name}: {e}",
            exc_info=True,
        )
        raise Exception(error_text)

def get_user_info(credentials: Credentials) -> Optional[Dict[str, Any]]:
    """Fetches basic user profile information (requires userinfo.email scope)."""
    if not credentials or not credentials.valid:
        logger.error("Cannot get user info: Invalid or missing credentials.")
        return None
    try:
        # Using googleapiclient discovery to get user info
        # Requires 'google-api-python-client' library
        service = build("oauth2", "v2", credentials=credentials)
        user_info = service.userinfo().get().execute()
        logger.info(f"Successfully fetched user info: {user_info.get('email')}")
        return user_info
    except HttpError as e:
        logger.error(f"HttpError fetching user info: {e.status_code} {e.reason}")
        # Handle specific errors, e.g., 401 Unauthorized might mean token issue
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching user info: {e}")
        return None


# --- Centralized Google Service Authentication ---


class GoogleAuthenticationError(Exception):
    """Exception raised when Google authentication is required or fails."""

    def __init__(self, message: str, auth_url: Optional[str] = None):
        super().__init__(message)
        self.auth_url = auth_url
