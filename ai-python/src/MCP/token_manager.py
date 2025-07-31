from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import httpx  # Make sure httpx is installed

from src.db.config import db_instance
from dotenv import load_dotenv
load_dotenv()
import os
# ---- Constants (replace with actual values) ----
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID",'12334214')
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET",'12334214')

collection = db_instance.get_collection("user")

# ---- DB Access Functions ----

def get_user(email: str) -> Optional[Dict[str, Any]]:
    """Fetch the user document from MongoDB."""
    return collection.find_one({"email": email})


def get_token_data(email: str, provider: str) -> Optional[Dict[str, Any]]:
    """Get tokenData for any provider."""
    user = get_user(email)
    if not user:
        print(f"⚠️ User not found: {email}")
        return None
    return user.get("mcpdata", {}).get(provider, {}).get("tokenData")


def is_token_expired(email: str, provider: str) -> bool:
    """Check if a given provider token is expired."""
    token_data = get_token_data(email, provider)
    if not token_data:
        print(f"⚠️ No token data for provider '{provider}'")
        return True

    user = get_user(email)
    timestamp = user.get("updatedAt") or user.get("createdAt")

    if not timestamp or not isinstance(timestamp, datetime):
        print("❌ Invalid or missing timestamp for user.")
        return True

    expires_in = token_data.get("expires_in", 0)
    if not isinstance(expires_in, int):
        print("❌ Invalid expires_in in token data.")
        return True

    expiry_time = timestamp + timedelta(seconds=expires_in - 60)  # proactive refresh
    now = datetime.now(timezone.utc)
    is_expired = now > expiry_time

    print(f"📆 {provider} token | created: {timestamp} | expires at: {expiry_time} | now: {now} | expired: {is_expired}")
    return is_expired


def get_access_token(email: str, provider: str) -> Optional[str]:
    return get_token_data(email, provider).get("access_token") if get_token_data(email, provider) else None


def get_refresh_token(email: str, provider: str) -> Optional[str]:
    return get_token_data(email, provider).get("refresh_token") if get_token_data(email, provider) else None


def get_all_token_info(email: str, provider: str) -> Optional[Dict[str, Any]]:
    return get_token_data(email, provider)


# ---- Token Save Handler ----

def save_tokens(email: str, provider: str, access_token: str, refresh_token: str, expires_in: int):
    """Save refreshed tokens to MongoDB."""
    collection.update_one(
        {"email": email},
        {
            "$set": {
                f"mcpdata.{provider}.tokenData.access_token": access_token,
                f"mcpdata.{provider}.tokenData.refresh_token": refresh_token,
                f"mcpdata.{provider}.tokenData.expires_in": expires_in,
                "CreatedAt": datetime.now(timezone.utc)
            }
        }
    )
    print(f"✅ Tokens updated for {email} | provider: {provider}")


# ---- Async Access Token Manager ----

async def get_valid_access_token(email: str, provider: str) -> str:
    """
    Returns a valid access token.
    - If refresh_token exists: check expiry and refresh if expired.
    - If no refresh_token: return current access_token without expiry check.
    """
    token_data = get_token_data(email, provider)
    if not token_data:
        raise Exception(f"❌ No token data found for {provider}")

    refresh_token = token_data.get("refresh_token")

    # ➤ Case 1: Refresh token is available → check expiry and refresh if needed
    if refresh_token:
        if not is_token_expired(email, provider):
            access_token = token_data.get("access_token")
            if access_token:
                return access_token
            else:
                raise Exception(f"❌ Access token missing for {provider} despite being valid")

        # Refresh the token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,  # currently only works for Google
                data={
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )

        token_data = response.json()

        if "access_token" not in token_data:
            raise Exception(f"❌ Failed to refresh access token: {token_data}")

        new_access_token = token_data["access_token"]
        new_expires_in = token_data.get("expires_in", 3600)

        save_tokens(email, provider, new_access_token, refresh_token, new_expires_in)
        return new_access_token

    # ➤ Case 2: No refresh token → just return current access token
    access_token = token_data.get("access_token")
    if access_token:
        print(f"🔓 Using static access token for {provider} (no refresh_token)")
        return access_token
    else:
        raise Exception(f"❌ Access token missing and no refresh token available for {provider}")
