# Slack MCP OAuth Configuration Setup

This guide will help you set up Slack OAuth integration for your Next.js application.

## 1. Environment Variables

Add the following environment variables to your `.env.local` file:

```env
# Slack OAuth Configuration
NEXT_PUBLIC_SLACK_CLIENT_ID=your_slack_client_id_here
SLACK_CLIENT_SECRET=your_slack_client_secret_here
NEXT_PUBLIC_SLACK_REDIRECT_URI=https://your-domain.com/api/slack/oauth/callback
```

## 2. Slack App Setup

### Step 1: Create a Slack App
1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App"
3. Choose "From scratch"
4. Enter your app name and select your workspace

### Step 2: Configure OAuth Settings
1. In your Slack app dashboard, go to "OAuth & Permissions"
2. Add the following redirect URL:
   ```
   https://your-domain.com/api/slack/oauth/callback
   ```
3. Add the following scopes:
   - `chat:write` - Send messages to channels
   - `channels:read` - View basic channel information
   - `channels:history` - View messages in public channels
   - `users:read` - View basic user information
   - `users:read.email` - View user email addresses

### Step 3: Install App to Workspace
1. Go to "Install App" in the sidebar
2. Click "Install to Workspace"
3. Authorize the app with the requested permissions

### Step 4: Get Credentials
1. Copy the "Client ID" from the "Basic Information" page
2. Copy the "Client Secret" from the "Basic Information" page
3. Add these to your environment variables

## 3. Backend API Endpoints

You'll need to implement these backend endpoints to handle Slack OAuth:

### GET /api/web/mcp/slack-connection
Check if user is connected to Slack

**Response:**
```json
{
  "isConnected": true,
  "team_name": "Your Team",
  "user_name": "John Doe"
}
```

### POST /api/web/mcp/slack-oauth-callback
Handle OAuth callback and store tokens

**Request Body:**
```json
{
  "access_token": "xoxb-...",
  "team_id": "T1234567890",
  "team_name": "Your Team",
  "user_id": "U1234567890",
  "scope": "chat:write,channels:read,...",
  "state": "random_state_string"
}
```

### POST /api/web/mcp/slack-disconnect
Disconnect Slack integration

**Request Body:**
```json
{
  "userId": "user_id_here"
}
```

### POST /api/web/mcp/slack-send-message
Send message to Slack channel

**Request Body:**
```json
{
  "channel": "#general",
  "message": "Hello from Weam!",
  "userId": "user_id_here"
}
```

## 4. Database Schema

You'll need to store Slack connection data. Here's a suggested schema:

```sql
CREATE TABLE slack_connections (
  id VARCHAR(255) PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  team_id VARCHAR(255) NOT NULL,
  team_name VARCHAR(255) NOT NULL,
  user_id_slack VARCHAR(255) NOT NULL,
  access_token TEXT NOT NULL,
  scope TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_team_id (team_id)
);
```

## 5. Security Considerations

1. **Token Storage**: Store access tokens securely in your database, encrypted if possible
2. **State Verification**: Always verify the OAuth state parameter to prevent CSRF attacks
3. **Token Refresh**: Implement token refresh logic for long-lived connections
4. **Error Handling**: Handle OAuth errors gracefully with user-friendly messages
5. **Rate Limiting**: Implement rate limiting for Slack API calls

## 6. Testing

1. Start your development server
2. Navigate to `/mcp` page
3. Click "Configure" on the Slack card
4. Click "Connect to Slack"
5. Complete the OAuth flow
6. Test sending a message to a channel

## 7. Troubleshooting

### Common Issues:

1. **"Invalid redirect URI"**: Make sure the redirect URI in your Slack app matches exactly
2. **"OAuth state mismatch"**: Check that the state parameter is being properly generated and verified
3. **"Access token not found"**: Ensure tokens are being stored correctly in your database
4. **"Permission denied"**: Verify that your Slack app has the correct scopes

### Debug Steps:

1. Check browser console for JavaScript errors
2. Check server logs for API errors
3. Verify environment variables are loaded correctly
4. Test Slack API endpoints directly with curl or Postman

## 8. Production Deployment

1. Update redirect URI to your production domain
2. Ensure all environment variables are set in production
3. Test the complete OAuth flow in production
4. Monitor Slack API rate limits
5. Set up error monitoring for OAuth failures

## 9. Additional Features

Consider implementing these additional features:

- **Channel List**: Show available channels to the user
- **Message Templates**: Pre-defined message templates
- **Scheduled Messages**: Send messages at specific times
- **Message History**: View sent messages
- **Team Management**: Handle multiple Slack workspaces
- **Webhook Support**: Receive notifications from Slack

## 10. Resources

- [Slack API Documentation](https://api.slack.com/)
- [Slack OAuth Documentation](https://api.slack.com/docs/oauth)
- [Slack Web API Methods](https://api.slack.com/web)
- [Slack App Manifest](https://api.slack.com/reference/manifests) 