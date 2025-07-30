import { encryptedData } from '@/utils/helper';
import { NextRequest, NextResponse } from 'next/server';
import { GITHUB } from '@/config/config';
import { updateMcpDataAction } from '@/actions/user';
import { MCP_CODES } from '@/components/Mcp/MCPAppList';

export async function GET(request: NextRequest) {
    console.log('GitHub OAuth callback received');
    console.log('Request URL:', request.url);
    
    try {
        // Check if required environment variables are set
        if (!GITHUB.CLIENT_ID || !GITHUB.CLIENT_SECRET) {
            console.error('Missing GitHub environment variables');
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_failed&reason=missing_env_vars`
            );
        }

        // Use URL constructor to avoid dynamic server usage
        const url = new URL(request.url);
        const code = url.searchParams.get('code');
        const state = url.searchParams.get('state');
        const error = url.searchParams.get('error');

        console.log('GitHub OAuth callback params:', {
            code: code ? 'present' : 'missing',
            state: state ? 'present' : 'missing',
            error: error || 'none'
        });

        if (error) {
            console.error('GitHub OAuth error:', error);
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_denied`
            );
        }

        if (!code || !state) {
            console.error('GitHub OAuth missing code or state');
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
        console.log('Token response status:', tokenResponse.status);
        //console.log('Token response:', tokenData);
        
        if (!tokenResponse.ok) {
            console.error('GitHub token exchange failed:', {
                status: tokenResponse.status,
                statusText: tokenResponse.statusText,
                data: tokenData
            });
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_failed&reason=token_exchange_failed&status=${tokenResponse.status}`
            );
        }
        
        if (tokenData.error) {
            console.error('GitHub OAuth error:', tokenData);
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_failed&reason=${tokenData.error_description || tokenData.error || 'unknown'}`
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
        // console.log('User info response status:', userResponse.status);
        // console.log('User info response:', userData);

        if (!userResponse.ok) {
            console.error('GitHub user info error:', {
                status: userResponse.status,
                statusText: userResponse.statusText,
                //data: userData
            });
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_failed&reason=user_info_error&status=${userResponse.status}`
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
        
        try {
            // console.log('Saving MCP data...');
            await updateMcpDataAction({ [mcpDataKey]: payload, isDeleted: false });
            // console.log('MCP data saved successfully');
        } catch (error) {
            // console.error('Error saving MCP data:', error);
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_failed&reason=mcp_data_save_error`
            );
        }

        return NextResponse.redirect(
            `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?success=github_connected&access_token=${tokenData.access_token}`
        );

    } catch (error) {
        console.error('GitHub OAuth callback error:', error);
        // console.error('Error details:', {
        //     message: error instanceof Error ? error.message : 'Unknown error',
        //     stack: error instanceof Error ? error.stack : undefined,
        //     name: error instanceof Error ? error.name : 'Unknown'
        // });
        return NextResponse.redirect(
            `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=github_oauth_error`
        );
    }
} 