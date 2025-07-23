"""Slack-related MCP tools."""
from typing import Any
from datetime import datetime
import httpx
from src.logger.default_logger import logger
SLACK_API_BASE = "https://slack.com/api"
async def make_slack_request(endpoint: str, bot_token: str, params: dict = None, json_data: dict = None, method: str = "GET") -> dict[str, Any] | None:
    """Make a request to the Slack API with proper error handling."""
    logger.debug(f"Making {method} request to Slack API: {endpoint}")
    headers = {
        "Authorization": f"Bearer {bot_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    url = f"{SLACK_API_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
            else:  # POST
                response = await client.post(url, headers=headers, json=json_data, timeout=30.0)
            response.raise_for_status()
            logger.debug(f"Successfully received response from Slack API: {endpoint}")
            return response.json()
        except Exception as e:
            logger.error(f"Error making request to Slack API: {endpoint} - Error: {str(e)}")
            return None
        
async def list_slack_channels(bot_token: str, limit: int = 100) -> str:
    """List all channels in the Slack workspace.

    Args:
        bot_token: Slack bot token
        limit: Maximum number of channels to return (default 100, max 1000)

    Returns:
        Formatted string containing channel information
    """
    logger.info(f"Listing Slack channels with limit: {limit}")
    params = {
        "limit": min(limit, 1000),  # Enforce maximum limit
        "exclude_archived": True
    }
    
    data = await make_slack_request("conversations.list", bot_token, params=params)
    
    if not data or not data.get("ok"):
        error = data.get("error", "unknown error") if data else "unknown error"
        logger.warning(f"Failed to list channels: {error}")
        return f"Failed to list channels: {error}"
    
    channels = data.get("channels", [])
    if not channels:
        logger.info("No channels found")
        return "No channels found in the workspace"
    
    formatted_channels = []
    for channel in channels:
        channel_info = f"""
        Name: #{channel.get('name', 'unknown')}
        ID: {channel.get('id', 'unknown')}
        Topic: {channel.get('topic', {}).get('value', 'No topic set')}
        Members: {channel.get('num_members', 0)}
        """
        formatted_channels.append(channel_info)
    
    logger.info(f"Returning {len(channels)} channels")
    return "\n---\n".join(formatted_channels)


async def send_slack_message(bot_token: str, channel_id: str, text: str) -> str:
    """Send a message to a Slack channel.

    Args:
        bot_token: Slack bot token
        channel_id: The ID of the channel to send the message to
        text: The message text to send

    Returns:
        Status message indicating success or failure
    """
    logger.info(f"Sending message to channel: {channel_id}")
    json_data = {
        "channel": channel_id,
        "text": text
    }
    
    data = await make_slack_request("chat.postMessage", bot_token, json_data=json_data, method="POST")
    
    if not data or not data.get("ok"):
        error = data.get("error", "unknown error") if data else "unknown error"
        logger.warning(f"Failed to send message: {error}")
        return f"Failed to send message: {error}"
    
    logger.info(f"Successfully sent message to channel: {channel_id}")
    return "Message sent successfully"


async def get_channel_messages(bot_token: str, channel_id: str, limit: int = 50) -> str:
    """Get recent messages from a Slack channel.

    Args:
        bot_token: Slack bot token
        channel_id: The ID of the channel to get messages from
        limit: Maximum number of messages to return (default 50, max 1000)

    Returns:
        Formatted string containing message history
    """
    logger.info(f"Getting messages from channel: {channel_id}")
    params = {
        "channel": channel_id,
        "limit": min(limit, 1000),  # Enforce maximum limit
        "inclusive": True,
        "include_all_metadata": True
    }
    
    data = await make_slack_request("conversations.history", bot_token, params=params)
    
    if not data or not data.get("ok"):
        error = data.get("error", "unknown error") if data else "unknown error"
        logger.warning(f"Failed to get channel messages: {error}")
        return f"Failed to get channel messages: {error}"
    
    messages = data.get("messages", [])
    if not messages:
        logger.info("No messages found in the channel")
        return "No messages found in the channel"
    
    # Get user info for all unique users in the messages
    user_ids = {msg.get("user") for msg in messages if msg.get("user")}
    user_names = {}
    
    for user_id in user_ids:
        user_data = await make_slack_request("users.info", bot_token, params={"user": user_id})
        if user_data and user_data.get("ok"):
            user = user_data.get("user", {})
            user_names[user_id] = user.get("real_name") or user.get("name", "Unknown")
    
    formatted_messages = []
    for msg in messages:
        # Convert timestamp to readable format
        ts = float(msg.get("ts", "0"))
        dt = datetime.fromtimestamp(ts)
        time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        # Get user name
        user_id = msg.get("user", "Unknown")
        user_name = user_names.get(user_id, "Unknown User")
        
        # Format message with reactions if any
        reactions = msg.get("reactions", [])
        reaction_str = ""
        if reactions:
            reaction_list = [f":{r['name']}: ({r['count']})" for r in reactions]
            reaction_str = f"\nReactions: {' '.join(reaction_list)}"
        
        # Format thread info if any
        thread_str = ""
        if msg.get("thread_ts") and msg.get("reply_count"):
            thread_str = f"\nThread: {msg.get('reply_count')} replies"
        
        message_text = f"""
Time: {time_str}
From: {user_name}
Message: {msg.get('text', '')}{"" if not reaction_str else reaction_str}{"" if not thread_str else thread_str}
        """
        formatted_messages.append(message_text)
    
    logger.info(f"Returning {len(messages)} messages from channel: {channel_id}")
    return "\n---\n".join(formatted_messages)
