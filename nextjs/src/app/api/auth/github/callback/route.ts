import { encryptedData } from '@/utils/helper';
import { NextRequest, NextResponse } from 'next/server';
import { GITHUB } from '@/config/config';
import { updateMcpDataAction } from '@/actions/user';
import { MCP_CODES } from '@/components/Mcp/MCPAppList';

export async function GET(request: NextRequest) {
    try {
        // Check if required environment variables are set
        if (!GITHUB.CLIENT_ID || !GITHUB.CLIENT_SECRET) {
            console.error('Missing GitHub environment variables');
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_failed&reason=missing_env_vars`
            );
        }

        const searchParams = request.nextUrl.searchParams;
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');

        if (error) {
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_denied`
            );
        }

        if (!code || !state) {
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_invalid`
            );
        }

        // Exchange code for access token
        const tokenResponse = await fetch(GITHUB.TOKEN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            body: JSON.stringify({
                client_id: GITHUB.CLIENT_ID,
                client_secret: GITHUB.CLIENT_SECRET,
                code: code,
                redirect_uri: GITHUB.REDIRECT_URI,
            }),
        });

        const tokenData = await tokenResponse.json();
        
        if (tokenData.error) {
            console.error('GitHub OAuth error:', tokenData);
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_failed&reason=${tokenData.error_description || 'unknown'}`
            );
        }

        // Get user information
        const userResponse = await fetch(GITHUB.USER_INFO_URL, {
            headers: {
                'Authorization': `Bearer ${tokenData.access_token}`,
                'Accept': 'application/vnd.github.v3+json',
            },
        });

        const userData = await userResponse.json();

        if (userResponse.status !== 200) {
            console.error('GitHub user info error:', userData);
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_failed&reason=user_info_error`
            );
        }

        const payload = {
            access_token: encryptedData(tokenData.access_token),
            token_type: tokenData.token_type,
            scope: tokenData.scope,
            user_id: userData.id,
            user_login: userData.login,
            user_name: userData.name,
            user_email: userData.email,
            user_avatar_url: userData.avatar_url,
            user_html_url: userData.html_url,
            state: state,
            has_user_token: !!tokenData.access_token,
        }
        
        const mcpDataKey = 'mcpdata.' + MCP_CODES.GITHUB;
        updateMcpDataAction({ [mcpDataKey]: payload, isDeleted: false });

        return NextResponse.redirect(
            `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?success=github_connected&access_token=${tokenData.access_token}`
        );

    } catch (error) {
        console.error('GitHub OAuth callback error:', error);
        return NextResponse.redirect(
            `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_error`
        );
    }
} 