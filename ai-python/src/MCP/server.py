"""Main MCP server application."""
import os
import argparse
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
from src.gateway.jwt_decode import get_user_by_id
from src.logger.default_logger import logger
from src.MCP.tools.slack.slack_tools import (
    list_slack_channels, send_slack_message, get_channel_messages,
    list_workspace_users, get_user_info, get_user_profile, get_channel_members,
    open_direct_message, send_direct_message, send_ephemeral_message,
    # Channel creation and management functions
    create_slack_channel, set_channel_topic, set_channel_purpose, archive_channel,
    invite_users_to_channel, kick_user_from_channel,
    # Thread management functions
    reply_to_thread, get_thread_replies, start_thread_with_message,
    reply_to_thread_with_broadcast, get_thread_info, find_threads_in_channel
)   
from fastapi import Request
from importlib import metadata
from fastapi.responses import JSONResponse
from datetime import datetime
# Load environment variables
load_dotenv()

mcp_port = os.getenv("MCP_SERVER_PORT", 8000)

# Initialize FastAPI app for health checks


# Initialize FastMCP server
mcp = FastMCP(
    "tools",  # Name of the MCP server
    host="0.0.0.0",  # Host address (0.0.0.0 allows connections from any IP)
    port=mcp_port,  # Port number for the server
)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request):
    """Health check endpoint for container orchestration."""
    try:
        version = metadata.version("workspace-mcp")
    except metadata.PackageNotFoundError:
        version = "dev"
    except Exception as e:
        version = f"error: {str(e)}"

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": "workspace-mcp",
            "version": version,
            "transport": "sse",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@mcp.tool()
async def slack_list_channels(limit: int = 100,mcp_data:str=None) -> str:
    """List all channels in the Slack workspace.

    Args:
        limit: Maximum number of channels to return (default 100, max 1000)
    """
    user_data = await get_user_by_id(mcp_data)

    return await list_slack_channels(user_data['mcpdata']['slack']['token'], limit)


@mcp.tool()
async def slack_send_message(channel_id: str, text: str,mcp_data:str=None) -> str:
    """Send a message to a Slack channel.

    Args:
        channel_id: The ID of the channel to send the message to
        text: The message text to send
    """
    user_data = await get_user_by_id(mcp_data)
    return await send_slack_message(user_data['mcpdata']['slack']['token'], channel_id, text)


@mcp.tool()
async def slack_get_messages(channel_name: str, limit: int = 50,mcp_data:str=None) -> str:
    """Get recent messages from a Slack channel.

    Args:
        channel_name: The Name of the channel to get messages from
        limit: Maximum number of messages to return (default 50, max 1000)
    """
    user_data = await get_user_by_id(mcp_data)
    return await get_channel_messages(user_data['mcpdata']['slack']['token'], channel_name, limit)


@mcp.tool()
async def slack_list_users(limit: int = 200, include_locale: bool = False,mcp_data:str=None) -> str:
    """List all users in the Slack workspace.

    Args:
        limit: Maximum number of users to return per page (default 200, max 200)
        include_locale: Whether to include user locale information
    """
    user_data = await get_user_by_id(mcp_data)    
    return await list_workspace_users(user_data['mcpdata']['slack']['token'], limit, include_locale)


@mcp.tool()
async def slack_get_user_info(user_id: str,mcp_data:str=None) -> str:
    """Get detailed information about a specific user.

    Args:
        user_id: The ID of the user to get information about
    """
    user_data = await get_user_by_id(mcp_data)
    return await get_user_info(user_data['mcpdata']['slack']['token'], user_id)


@mcp.tool()
async def slack_get_user_profile(user_id: str,mcp_data:str=None) -> str:
    """Get user profile information including custom fields.

    Args:
        user_id: The ID of the user to get profile for
    """
    user_data = await get_user_by_id(mcp_data)
    return await get_user_profile(user_data['mcpdata']['slack']['token'], user_id)


@mcp.tool()
async def slack_get_channel_members(channel_id: str, limit: int = 200,mcp_data:str=None) -> str:
    """Get all members of a specific channel.

    Args:
        channel_id: The ID of the channel
        limit: Maximum number of members to return per page
    """
    user_data = await get_user_by_id(mcp_data)
    return await get_channel_members(user_data['mcpdata']['slack']['token'], channel_id, limit)


@mcp.tool()
async def slack_open_dm(user_ids: list[str],mcp_data:str=None) -> str:
    """Open a direct message or multi-person direct message.

    Args:
        user_ids: List of user IDs (1 for DM, multiple for MPIM)
    """
    user_data = await get_user_by_id(mcp_data)
    return await open_direct_message(user_data['mcpdata']['slack']['token'], user_ids)


@mcp.tool()
async def slack_send_dm(user_id: str, text: str,mcp_data:str=None) -> str:
    """Send a direct message to a user.

    Args:
        user_id: The ID of the user to send DM to
        text: The message text to send
    """
    user_data = await get_user_by_id(mcp_data)
    return await send_direct_message(user_data['mcpdata']['slack']['token'], user_id, text)


@mcp.tool()
async def slack_send_ephemeral_message(channel_id: str, user_id: str, text: str,mcp_data:str=None) -> str:
    """Send an ephemeral message visible only to a specific user.

    Args:
        channel_id: The ID of the channel
        user_id: The ID of the user who will see the message
        text: The message text to send
    """
    user_data = await get_user_by_id(mcp_data)
    return await send_ephemeral_message(user_data['mcpdata']['slack']['token'], channel_id, user_id, text)


# =============================================================================
# CHANNEL CREATION AND MANAGEMENT TOOLS
# =============================================================================

@mcp.tool()
async def slack_create_channel(
    channel_name: str, 
    is_private: bool = False, 
    topic: str = None, 
    purpose: str = None, 
    initial_members: list[str] = None,
    mcp_data:str=None
) -> str:
    """Create a new Slack channel.

    Args:
        channel_name: Name of the channel to create (without # symbol)
        is_private: Whether to create a private channel (default: False for public)
        topic: Optional topic for the channel
        purpose: Optional purpose description for the channel
        initial_members: Optional list of user IDs to invite to the channel
    """
    user_data = await get_user_by_id(mcp_data)
    return await create_slack_channel(
        user_data['mcpdata']['slack']['token'], 
        channel_name, 
        is_private, 
        topic, 
        purpose, 
        initial_members
    )


@mcp.tool()
async def slack_set_channel_topic(channel_id: str, topic: str,mcp_data:str=None) -> str:
    """Set or update the topic for a Slack channel.

    Args:
        channel_id: The ID of the channel
        topic: New topic for the channel
    """
    user_data = await get_user_by_id(mcp_data)
    return await set_channel_topic(user_data['mcpdata']['slack']['token'], channel_id, topic)


@mcp.tool()
async def slack_set_channel_purpose(channel_id: str, purpose: str,mcp_data:str=None) -> str:
    """Set or update the purpose for a Slack channel.

    Args:
        channel_id: The ID of the channel
        purpose: New purpose for the channel
    """
    user_data = await get_user_by_id(mcp_data)
    return await set_channel_purpose(mcp['slack']['token'], channel_id, purpose)


@mcp.tool()
async def slack_archive_channel(channel_id: str,mcp_data:str=None) -> str:
    """Archive a Slack channel.

    Args:
        channel_id: The ID of the channel to archive
    """
    user_data = await get_user_by_id(mcp_data)
    return await archive_channel(user_data['mcpdata']['slack']['token'], channel_id)


@mcp.tool()
async def slack_invite_users_to_channel(channel_id: str, user_ids: list[str],mcp_data:str=None) -> str:
    """Invite users to a Slack channel.

    Args:
        channel_id: The ID of the channel
        user_ids: List of user IDs to invite
    """
    user_data = await get_user_by_id(mcp_data)
    return await invite_users_to_channel(user_data['mcpdata']['slack']['token'], channel_id, user_ids)


@mcp.tool()
async def slack_kick_user_from_channel(channel_id: str, user_id: str,mcp_data:str=None) -> str:
    """Remove a user from a Slack channel.

    Args:
        channel_id: The ID of the channel
        user_id: The ID of the user to remove
    """
    user_data = await get_user_by_id(mcp_data)
    return await kick_user_from_channel(user_data['mcpdata']['slack']['token'], channel_id, user_id)



# =============================================================================
# THREAD MANAGEMENT TOOLS - ADD TO YOUR MAIN MCP SERVER FILE
# =============================================================================


@mcp.tool()
async def slack_reply_to_thread(channel_id: str, thread_ts: str, text: str,mcp_data:str=None) -> str:
    """Reply to an existing thread in a Slack channel.

    Args:
        channel_id: The ID of the channel containing the thread
        thread_ts: The timestamp of the parent message (thread identifier)
        text: The reply text to send
    """
    user_data = await get_user_by_id(mcp_data)
    return await reply_to_thread(user_data['mcpdata']['slack']['token'], channel_id, thread_ts, text)


@mcp.tool()
async def slack_get_thread_replies(channel_id: str, thread_ts: str, limit: int = 100,mcp_data:str=None) -> str:
    """Get all replies in a specific thread.

    Args:
        channel_id: The ID of the channel containing the thread
        thread_ts: The timestamp of the parent message (thread identifier)
        limit: Maximum number of replies to return (default 100, max 1000)
    """
    user_data = await get_user_by_id(mcp_data)
    return await get_thread_replies(user_data['mcpdata']['slack']['token'], channel_id, thread_ts, limit)


@mcp.tool()
async def slack_start_thread(channel_id: str, text: str, broadcast: bool = False,mcp_data:str=None) -> str:
    """Send a message that can be used to start a thread.

    Args:
        channel_id: The ID of the channel to send the message to
        text: The message text to send
        broadcast: Whether to broadcast the thread reply to the channel (default: False)
    """
    user_data = await get_user_by_id(mcp_data)
    return await start_thread_with_message(user_data['mcpdata']['slack']['token'], channel_id, text, broadcast)


@mcp.tool()
async def slack_reply_to_thread_with_broadcast(channel_id: str, thread_ts: str, text: str,mcp_data:str=None) -> str:
    """Reply to a thread and broadcast the reply to the channel.

    Args:
        channel_id: The ID of the channel containing the thread
        thread_ts: The timestamp of the parent message (thread identifier)
        text: The reply text to send
    """
    user_data = await get_user_by_id(mcp_data)
    return await reply_to_thread_with_broadcast(user_data['mcpdata']['slack']['token'], channel_id, thread_ts, text)


@mcp.tool()
async def slack_get_thread_info(channel_id: str, thread_ts: str,mcp_data:str=None) -> str:
    """Get summary information about a thread.

    Args:
        channel_id: The ID of the channel containing the thread
        thread_ts: The timestamp of the parent message (thread identifier)
    """
    user_data = await get_user_by_id(mcp_data)
    return await get_thread_info(user_data['mcpdata']['slack']['token'], channel_id, thread_ts)


@mcp.tool()
async def slack_find_threads_in_channel(channel_id: str, limit: int = 50,mcp_data:str=None) -> str:
    """Find all messages that have threads (replies) in a channel.

    Args:
        channel_id: The ID of the channel to search
        limit: Maximum number of messages to check (default 50, max 1000)
    """
    user_data = await get_user_by_id(mcp_data)
    return await find_threads_in_channel(user_data['mcpdata']['slack']['token'], channel_id, limit)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')