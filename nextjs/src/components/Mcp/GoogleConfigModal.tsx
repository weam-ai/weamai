'use client';

import { useEffect } from 'react';
import { useGoogleOAuth } from '@/hooks/mcp/useGoogleOAuth';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from '@/components/ui/dialog';
import { ConfigurationButton, DisconnectButton } from './Shared';
import Toast from '@/utils/toast';
import { useSearchParams } from 'next/navigation';

type GoogleConfigModalProps = {
    isOpen: boolean;
    onClose: () => void;
    mcpIcon: React.ReactNode;
    title: string;
    description: string;
};

const GoogleConfigModal: React.FC<GoogleConfigModalProps> = ({
    isOpen,
    onClose,
    mcpIcon,
    title,
    description,
}) => {
    const searchParams = useSearchParams();
    const { isConnected, loading, initiateGoogleOAuth, disconnectGoogle } =
        useGoogleOAuth();

    const handleConnect = () => {
        initiateGoogleOAuth(title);
    };

    const handleDisconnect = async () => {
        await disconnectGoogle();
        onClose();
    };

    useEffect(() => {
        const success = searchParams.get('success');
        const error = searchParams.get('error');
        const accessToken = searchParams.get('access_token');
        const userData = searchParams.get('user_data');

        if (success === 'google_connected' && accessToken) {
            // Store the access token in localStorage
            localStorage.setItem('google_access_token', accessToken);
            
            // Store user data if provided
            if (userData) {
                try {
                    const decodedUserData = JSON.parse(decodeURIComponent(userData));
                    localStorage.setItem('google_user_data', JSON.stringify(decodedUserData));
                } catch (error) {
                    console.error('Error parsing user data:', error);
                }
            }
            
            // Show success toast
            Toast('Successfully connected to Google!');
            
            // Clean up URL parameters
            window.history.replaceState({}, document.title, window.location.pathname);
        } else if (error === 'google_oauth_error') {
            // Show error toast
            Toast('Failed to connect to Google. Please try again.', 'error');
            
            // Clean up URL parameters
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }, [searchParams]);

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="md:max-w-[600px] max-w-[calc(100%-30px)] py-7 border-none">
                <DialogHeader className="px-[30px] pb-5 border-b">
                    <div className="flex items-center gap-3">
                        {mcpIcon}
                        <div>
                            <DialogTitle className="font-bold text-font-20">{`Configure to ${title}`}</DialogTitle>
                            <DialogDescription className="!text-b6 text-font-14">
                                {description}
                            </DialogDescription>
                        </div>
                    </div>
                </DialogHeader>

                <div className="px-5 md:px-10 py-5">
                    {!isConnected ? (
                        <ConfigurationButton
                            title={title}
                            description={description}
                            handleConnect={handleConnect}
                            loading={loading}
                        />
                    ) : (
                        <DisconnectButton
                            title={title}
                            description={description}
                            handleDisconnect={handleDisconnect}
                            loading={loading}
                        />
                    )}
                </div>

                <DialogFooter className="flex items-center justify-center gap-2.5 pb-[30px] px-[30px]">
                    <button className="btn btn-outline-black" onClick={onClose}>
                        Close
                    </button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};

export default GoogleConfigModal;
