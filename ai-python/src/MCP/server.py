"""Main MCP server application."""
import os
import argparse
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
from src.logger.default_logger import logger
from src.MCP.tools.slack.slack_tools import list_slack_channels, send_slack_message,get_channel_messages   

# Load environment variables
load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

# Initialize FastAPI app for health checks
app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Initialize FastMCP server
mcp = FastMCP(
    "tools",  # Name of the MCP server
    host="0.0.0.0",  # Host address (0.0.0.0 allows connections from any IP)
    port=8000,  # Port number for the server
    app=app,  # Pass the FastAPI app for additional endpoints
)


@mcp.tool()
async def slack_list_channels(limit: int = 100) -> str:
    """List all channels in the Slack workspace.

    Args:
        limit: Maximum number of channels to return (default 100, max 1000)
    """
    return await list_slack_channels(SLACK_BOT_TOKEN, limit)


@mcp.tool()
async def slack_send_message(channel_id: str, text: str) -> str:
    """Send a message to a Slack channel.

    Args:
        channel_id: The ID of the channel to send the message to
        text: The message text to send
    """
    return await send_slack_message(SLACK_BOT_TOKEN, channel_id, text)


@mcp.tool()
async def slack_get_messages(channel_id: str, limit: int = 50) -> str:
    """Get recent messages from a Slack channel.

    Args:
        channel_id: The ID of the channel to get messages from
        limit: Maximum number of messages to return (default 50, max 1000)
    """
    return await get_channel_messages(SLACK_BOT_TOKEN, channel_id, limit)

# @mcp.tool()
# async def weather_get_alerts(state: str) -> str:
#     """Get weather alerts for a US state.

#     Args:
#         state: Two-letter US state code (e.g. CA, NY)
#     """
#     return await get_alerts(state)


# @mcp.tool()
# async def weather_get_forecast(latitude: float, longitude: float) -> str:
#     """Get weather forecast for a location.

#     Args:
#         latitude: Latitude of the location
#         longitude: Longitude of the location
#     """
#     return await get_forecast(latitude, longitude)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')
