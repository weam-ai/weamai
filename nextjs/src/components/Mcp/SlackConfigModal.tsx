'use client';

import React, { useState, useEffect } from 'react';
import { useSlackOAuth } from '@/hooks/mcp/useSlackOAuth';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import Label from '@/widgets/Label';
import SlackIcon from '@/icons/SlackIcon';
import Toast from '@/utils/toast';

interface SlackConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const SlackConfigModal: React.FC<SlackConfigModalProps> = ({ isOpen, onClose }) => {
    const {
        isConnected,
        loading,
        connectionData,
        initiateSlackOAuth,
        disconnectSlack,
        sendTestMessage
    } = useSlackOAuth();

    const [testChannel, setTestChannel] = useState('');
    const [testMessage, setTestMessage] = useState('Hello from Weam! This is a test message.');
    const [sendingTest, setSendingTest] = useState(false);

    const handleConnect = () => {
        initiateSlackOAuth();
    };

    const handleDisconnect = async () => {
        await disconnectSlack();
        onClose();
    };

    const handleSendTestMessage = async () => {
        if (!testChannel.trim()) {
            Toast('Please enter a channel name', 'error');
            return;
        }

        setSendingTest(true);
        try {
            await sendTestMessage(testChannel, testMessage);
        } finally {
            setSendingTest(false);
        }
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="md:max-w-[600px] max-w-[calc(100%-30px)] py-7 border-none">
                <DialogHeader className="px-[30px] pb-5 border-b">
                    <div className="flex items-center gap-3">
                        <SlackIcon className="size-6" />
                        <div>
                            <DialogTitle className="font-bold text-font-20">Configure Slack</DialogTitle>
                            <DialogDescription className="!text-b6 text-font-14">
                                Connect your Slack workspace to enable real-time notifications and team collaboration.
                            </DialogDescription>
                        </div>
                    </div>
                </DialogHeader>

                <div className="px-5 md:px-10 py-5">
                    {!isConnected ? (
                        <div className="space-y-4">
                            <div className="bg-b2/10 p-4 rounded-lg">
                                <h3 className="font-semibold text-font-16 mb-2">Connect to Slack</h3>
                                <p className="text-b6 text-font-14 mb-4">
                                    Connect your Slack workspace to send messages, receive notifications, and collaborate with your team.
                                </p>
                                <button
                                    className="btn btn-black w-full"
                                    onClick={handleConnect}
                                    disabled={loading}
                                >
                                    {loading ? 'Connecting...' : 'Connect to Slack'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Connection Status */}
                            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                                <div className="flex items-center gap-2 mb-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    <span className="font-semibold text-green-800">Connected to Slack</span>
                                </div>
                                {connectionData && (
                                    <div className="text-sm text-green-700">
                                        <p>Team: {connectionData.team_name}</p>
                                        <p>User: {connectionData.user_name}</p>
                                    </div>
                                )}
                            </div>

                            {/* Test Message Section */}
                            <div className="space-y-4">
                                <h3 className="font-semibold text-font-16">Send Test Message</h3>
                                
                                <div>
                                    <Label title="Channel" htmlFor="testChannel">
                                        Channel Name (e.g., #general)
                                    </Label>
                                    <input
                                        id="testChannel"
                                        type="text"
                                        className="default-form-input"
                                        placeholder="#general"
                                        value={testChannel}
                                        onChange={(e) => setTestChannel(e.target.value)}
                                    />
                                </div>

                                <div>
                                    <Label title="Message" htmlFor="testMessage">
                                        Test Message
                                    </Label>
                                    <textarea
                                        id="testMessage"
                                        className="default-form-input"
                                        rows={3}
                                        value={testMessage}
                                        onChange={(e) => setTestMessage(e.target.value)}
                                        placeholder="Enter your test message..."
                                    />
                                </div>

                                <button
                                    className="btn btn-outline-black w-full"
                                    onClick={handleSendTestMessage}
                                    disabled={sendingTest || !testChannel.trim()}
                                >
                                    {sendingTest ? 'Sending...' : 'Send Test Message'}
                                </button>
                            </div>

                            {/* Disconnect Section */}
                            <div className="border-t pt-4">
                                <h3 className="font-semibold text-font-16 mb-3 text-red-600">Danger Zone</h3>
                                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                                    <p className="text-red-700 text-sm mb-3">
                                        Disconnecting will remove all Slack integrations and stop all notifications.
                                    </p>
                                    <button
                                        className="btn btn-outline-red"
                                        onClick={handleDisconnect}
                                        disabled={loading}
                                    >
                                        {loading ? 'Disconnecting...' : 'Disconnect Slack'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <DialogFooter className="flex items-center justify-center gap-2.5 pb-[30px] px-[30px]">
                    <button
                        className="btn btn-outline-black"
                        onClick={onClose}
                    >
                        Close
                    </button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};

export default SlackConfigModal; 