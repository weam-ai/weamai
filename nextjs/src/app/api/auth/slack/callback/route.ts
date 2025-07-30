import { NextRequest, NextResponse } from 'next/server';
import { SLACK } from '@/config/config';
import { updateMcpDataAction } from '@/actions/user';
import { MCP_CODES } from '@/components/Mcp/MCPAppList';
import { encryptedData } from '@/utils/helper';

// Force dynamic rendering for this route
export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
    try {
        // Check if required environment variables are set
        if (!SLACK.CLIENT_ID || !SLACK.CLIENT_SECRET) {
            console.error('Missing Slack environment variables');
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=slack_oauth_failed&reason=missing_env_vars`
            );
        }

        const searchParams = request.nextUrl.searchParams;
        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');

        if (error) {
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=slack_oauth_denied`
            );
        }

        if (!code || !state) {
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=slack_oauth_invalid`
            );
        }

        const tokenResponse = await fetch(SLACK.TOKEN_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                client_id: SLACK.CLIENT_ID,
                client_secret: SLACK.CLIENT_SECRET,
                code: code,
                redirect_uri: SLACK.REDIRECT_URI,
            }),
        });

        const tokenData = await tokenResponse.json();
        
        if (!tokenData.ok) {
            console.error('Slack OAuth error:', tokenData);
            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=slack_oauth_failed&reason=${tokenData.error || 'unknown'}`
            );
        } else {
            console.log('Slack OAuth successful - processing token data...');

            const payload = {
                access_token: encryptedData(tokenData.authed_user?.access_token), // Bot token
                user_access_token: tokenData.authed_user?.access_token || null, // User token (might be null)
                team_id: tokenData.team?.id,
                team_name: tokenData.team?.name,
                user_id: tokenData.authed_user?.id,
                user_scope: tokenData.authed_user?.scope || null,
                state: state,
                token_type: tokenData.token_type
            }
            
            const mcpDataKey = 'mcpdata.' + MCP_CODES.SLACK;
            updateMcpDataAction({ [mcpDataKey]: payload, isDeleted: false });

            return NextResponse.redirect(
                `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?success=slack_connected`
            );
        }        

    } catch (error) {
        console.error('Slack OAuth callback error:', error);
        return NextResponse.redirect(
            `${process.env.NEXT_PUBLIC_DOMAIN_URL}/mcp?error=slack_oauth_error`
        );
    }
} 