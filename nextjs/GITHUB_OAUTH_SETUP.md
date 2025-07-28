# GitHub MCP OAuth Configuration Setup

This guide will help you set up GitHub OAuth integration for your Next.js application.

## 1. Environment Variables

Add the following environment variables to your `.env.local` file:

```env
# GitHub OAuth Configuration
NEXT_PUBLIC_GITHUB_CLIENT_ID=your_github_client_id_here
NEXT_PUBLIC_GITHUB_CLIENT_SECRET=your_github_client_secret_here
NEXT_PUBLIC_GITHUB_REDIRECT_URI=https://your-domain.com/api/auth/github/callback
```

## 2. GitHub App Setup

### Step 1: Create a GitHub OAuth App
1. Go to [https://github.com/settings/developers](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Fill in the application details:
   - **Application name**: Your app name (e.g., "Weam AI")
   - **Homepage URL**: Your domain URL (e.g., `https://your-domain.com`)
   - **Application description**: Brief description of your app
   - **Authorization callback URL**: `https://your-domain.com/api/auth/github/callback`

### Step 2: Configure OAuth Scopes
The GitHub OAuth app will request the following scopes:
- `repo` - Full control of private repositories
- `user` - Read access to user profile
- `read:org` - Read access to organization data
- `write:org` - Write access to organization data
- `admin:org` - Full control of organizations
- `delete_repo` - Delete repositories
- `workflow` - Update GitHub Action workflows

### Step 3: Get Credentials
1. After creating the OAuth app, you'll get a **Client ID**
2. Click "Generate a new client secret" to get the **Client Secret**
3. Add these to your environment variables

## 3. Backend API Endpoints

You'll need to implement these backend endpoints to handle GitHub OAuth:

### GET /api/web/mcp/github-connection
Check if user is connected to GitHub

**Response:**
```json
{
  "isConnected": true,
  "user_name": "John Doe",
  "user_login": "johndoe",
  "user_email": "john@example.com"
}
```

### POST /api/web/mcp/github-oauth-callback
Handle OAuth callback and store tokens

**Request Body:**
```json
{
  "access_token": "ghp_...",
  "token_type": "bearer",
  "scope": "repo,user,read:org,write:org,admin:org,delete_repo,workflow",
  "user_id": 123456,
  "user_login": "johndoe",
  "user_name": "John Doe",
  "user_email": "john@example.com",
  "user_avatar_url": "https://avatars.githubusercontent.com/u/123456?v=4",
  "user_html_url": "https://github.com/johndoe",
  "state": "random_state_string"
}
```

### POST /api/web/mcp/github-disconnect
Disconnect GitHub integration

**Request Body:**
```json
{
  "userId": "user_id_here"
}
```

### POST /api/web/mcp/github-create-issue
Create issue in GitHub repository

**Request Body:**
```json
{
  "repo": "owner/repo",
  "title": "Issue Title",
  "body": "Issue description",
  "userId": "user_id_here"
}
```

### POST /api/web/mcp/github-create-pr
Create pull request in GitHub repository

**Request Body:**
```json
{
  "repo": "owner/repo",
  "title": "PR Title",
  "body": "PR description",
  "head": "feature-branch",
  "base": "main",
  "userId": "user_id_here"
}
```

## 4. Database Schema

You'll need to store GitHub connection data. Here's a suggested schema:

```sql
CREATE TABLE github_connections (
  id VARCHAR(255) PRIMARY KEY,
  user_id VARCHAR(255) NOT NULL,
  github_user_id INT NOT NULL,
  github_user_login VARCHAR(255) NOT NULL,
  github_user_name VARCHAR(255),
  github_user_email VARCHAR(255),
  github_user_avatar_url TEXT,
  github_user_html_url TEXT,
  access_token TEXT NOT NULL,
  token_type VARCHAR(50) NOT NULL,
  scope TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_github_user_id (github_user_id)
);
```

## 5. Security Considerations

1. **Token Storage**: Store access tokens securely in your database, encrypted if possible
2. **State Verification**: Always verify the OAuth state parameter to prevent CSRF attacks
3. **Token Refresh**: GitHub tokens don't expire, but implement proper token management
4. **Error Handling**: Handle OAuth errors gracefully with user-friendly messages
5. **Rate Limiting**: Implement rate limiting for GitHub API calls (5000 requests per hour for authenticated users)
6. **Scope Management**: Only request the scopes you actually need

## 6. Testing

1. Start your development server
2. Navigate to `/mcp` page
3. Click "Configure" on the GitHub card
4. Click "Connect to GitHub"
5. Complete the OAuth flow
6. Test creating an issue or pull request

## 7. Troubleshooting

### Common Issues:

1. **"Invalid redirect URI"**: Make sure the redirect URI in your GitHub OAuth app matches exactly
2. **"OAuth state mismatch"**: Check that the state parameter is being properly generated and verified
3. **"Insufficient scopes"**: Ensure your OAuth app has the required scopes configured
4. **"Rate limit exceeded"**: Implement proper rate limiting and caching for GitHub API calls

## 8. GitHub API Rate Limits

- **Authenticated requests**: 5,000 requests per hour
- **Unauthenticated requests**: 60 requests per hour
- **Search API**: 30 requests per minute for authenticated users

## 9. Implementation Files

The following files have been created for GitHub OAuth integration:

1. **`src/config/config.ts`** - Added GitHub OAuth configuration
2. **`src/app/api/auth/github/callback/route.ts`** - GitHub OAuth callback handler
3. **`src/hooks/mcp/useGitHubOAuth.ts`** - GitHub OAuth hook for React components
4. **`src/components/Mcp/GitHubConfigModal.tsx`** - GitHub configuration modal component

## 10. Usage Example

```typescript
import { useGitHubOAuth } from '@/hooks/mcp/useGitHubOAuth';

const MyComponent = () => {
    const { isConnected, initiateGitHubOAuth, disconnectGitHub } = useGitHubOAuth();

    return (
        <div>
            {isConnected ? (
                <button onClick={disconnectGitHub}>Disconnect GitHub</button>
            ) : (
                <button onClick={initiateGitHubOAuth}>Connect GitHub</button>
            )}
        </div>
    );
};
``` 