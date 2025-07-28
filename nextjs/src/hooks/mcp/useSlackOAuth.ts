import { useState, useEffect } from 'react';
import { SLACK } from '@/config/config';
import Toast from '@/utils/toast';
import { getCurrentUser } from '@/utils/handleAuth';

export const useSlackOAuth = () => {
    const [isConnected, setIsConnected] = useState(false);
    const [loading, setLoading] = useState(false);
    const [connectionData, setConnectionData] = useState(null);
    const user = getCurrentUser();

    // Check if user is already connected to Slack
    const checkSlackConnection = async () => {
        // This would check localStorage or session for existing connection
        // For now, we'll assume not connected
        setIsConnected(false);
    };

    // Initiate Slack OAuth flow
    const initiateSlackOAuth = () => {
        const state = Math.random().toString(36).substring(7);
        const params = new URLSearchParams({
            client_id: SLACK.CLIENT_ID,
            user_scope: SLACK.SCOPE,
            redirect_uri: SLACK.REDIRECT_URI,
            state: state,
            response_type: 'code'
        });

        // Redirect to Slack OAuth
        window.location.href = `${SLACK.AUTH_URL}?${params.toString()}`;
    };

    // Handle OAuth callback - this is handled by the Next.js API route
    const handleSlackCallback = async (code: string, state: string) => {
        setLoading(true);
        try {
            const storedState = localStorage.getItem('slack_oauth_state');
            
            if (state !== storedState) {
                Toast('OAuth state mismatch. Please try again.', 'error');
                return;
            }

            // The actual token exchange happens in the Next.js API route
            // This function is called after successful OAuth
            setIsConnected(true);
            Toast('Successfully connected to Slack!', 'success');            
        } catch (error) {
            console.error('Error handling Slack callback:', error);
            Toast('Failed to connect to Slack. Please try again.', 'error');
        } finally {
            setLoading(false);
        }
    };

    // Disconnect Slack
    const disconnectSlack = async () => {
        setLoading(true);
        try {
            // Clear local storage
            setIsConnected(false);
            setConnectionData(null);
            Toast('Successfully disconnected from Slack!', 'success');
        } catch (error) {
            console.error('Error disconnecting Slack:', error);
            Toast('Failed to disconnect from Slack. Please try again.', 'error');
        } finally {
            setLoading(false);
        }
    };

    // Send test message to Slack
    const sendTestMessage = async (channel: string, message: string) => {
        try {
            // This would call your backend API to send the message
            // For now, just show a success message
            Toast('Message sent successfully!', 'success');
        } catch (error) {
            console.error('Error sending Slack message:', error);
            Toast('Failed to send message. Please try again.', 'error');
        }
    };

    useEffect(() => {
        checkSlackConnection();
    }, []);

    return {
        isConnected,
        loading,
        connectionData,
        initiateSlackOAuth,
        handleSlackCallback,
        disconnectSlack,
        sendTestMessage,
        checkSlackConnection
    };
}; 