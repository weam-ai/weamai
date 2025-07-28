'use client';

import React, { useState, useEffect } from 'react';
import { useGitHubOAuth } from '@/hooks/mcp/useGitHubOAuth';
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
} from "@/components/ui/dialog";
import Label from '@/widgets/Label';
import GitHubIcon from '@/icons/GitHubIcon';
import Toast from '@/utils/toast';
import { useSearchParams } from 'next/navigation';

interface GitHubConfigModalProps {
    isOpen: boolean;
    onClose: () => void;
}

const GitHubConfigModal: React.FC<GitHubConfigModalProps> = ({ isOpen, onClose }) => {
    const {
        isConnected,
        loading,
        connectionData,
        initiateGitHubOAuth,
        disconnectGitHub,
        createTestIssue
    } = useGitHubOAuth();

    const [testRepo, setTestRepo] = useState('');
    const [testIssueTitle, setTestIssueTitle] = useState('Test Issue from Weam');
    const [testIssueBody, setTestIssueBody] = useState('This is a test issue created via Weam AI integration.');
    const [creatingTest, setCreatingTest] = useState(false);
    const searchParams = useSearchParams();

    const handleConnect = () => {
        initiateGitHubOAuth();
    };

    const handleDisconnect = async () => {
        await disconnectGitHub();
        onClose();
    };

    const handleCreateTestIssue = async () => {
        if (!testRepo.trim()) {
            Toast('Please enter a repository name (owner/repo)', 'error');
            return;
        }

        setCreatingTest(true);
        try {
            await createTestIssue(testRepo, testIssueTitle, testIssueBody);
        } finally {
            setCreatingTest(false);
        }
    };

    useEffect(() => {
        const success = searchParams.get('success');
        const error = searchParams.get('error');
        const accessToken = searchParams.get('access_token');

        if (success === 'github_connected' && accessToken) {
            // Store the access token in localStorage
            localStorage.setItem('github_access_token', accessToken);
            
            // Show success toast
            Toast('Successfully connected to GitHub!');
            
            // Clean up URL parameters
            window.history.replaceState({}, document.title, window.location.pathname);
        } else if (error && error.startsWith('github_oauth_')) {
            // Show error toast
            Toast('Failed to connect to GitHub. Please try again.', 'error');
            
            // Clean up URL parameters
            window.history.replaceState({}, document.title, window.location.pathname);
        }
    }, [searchParams]);

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="md:max-w-[600px] max-w-[calc(100%-30px)] py-7 border-none">
                <DialogHeader className="px-[30px] pb-5 border-b">
                    <div className="flex items-center gap-3">
                        <GitHubIcon className="size-6" />
                        <div>
                            <DialogTitle className="font-bold text-font-20">Configure GitHub</DialogTitle>
                            <DialogDescription className="!text-b6 text-font-14">
                                Connect your GitHub account to enable repository automation and issue management.
                            </DialogDescription>
                        </div>
                    </div>
                </DialogHeader>

                <div className="px-5 md:px-10 py-5">
                    {!isConnected ? (
                        <div className="space-y-4">
                            <div className="bg-b2/10 p-4 rounded-lg">
                                <h3 className="font-semibold text-font-16 mb-2">Connect to GitHub</h3>
                                <p className="text-b6 text-font-14 mb-4">
                                    Connect your GitHub account to create issues, manage pull requests, and automate repository operations.
                                </p>
                                <button
                                    className="btn btn-black w-full"
                                    onClick={handleConnect}
                                    disabled={loading}
                                >
                                    {loading ? 'Connecting...' : 'Connect to GitHub'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Connection Status */}
                            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                                <div className="flex items-center gap-2 mb-2">
                                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                    <span className="font-semibold text-green-800">Connected to GitHub</span>
                                </div>
                                {connectionData && (
                                    <div className="text-sm text-green-700">
                                        <p>User: {connectionData.user_name || connectionData.user_login}</p>
                                        <p>Email: {connectionData.user_email}</p>
                                    </div>
                                )}
                            </div>

                            {/* Test Issue Section */}
                            <div className="space-y-4">
                                <h3 className="font-semibold text-font-16">Create Test Issue</h3>
                                
                                <div>
                                    <Label title="Repository" htmlFor="testRepo">
                                        Repository (owner/repo)
                                    </Label>
                                    <input
                                        id="testRepo"
                                        type="text"
                                        className="default-form-input"
                                        placeholder="owner/repository"
                                        value={testRepo}
                                        onChange={(e) => setTestRepo(e.target.value)}
                                    />
                                </div>

                                <div>
                                    <Label title="Issue Title" htmlFor="testIssueTitle">
                                        Issue Title
                                    </Label>
                                    <input
                                        id="testIssueTitle"
                                        type="text"
                                        className="default-form-input"
                                        value={testIssueTitle}
                                        onChange={(e) => setTestIssueTitle(e.target.value)}
                                        placeholder="Enter issue title..."
                                    />
                                </div>

                                <div>
                                    <Label title="Issue Description" htmlFor="testIssueBody">
                                        Issue Description
                                    </Label>
                                    <textarea
                                        id="testIssueBody"
                                        className="default-form-input"
                                        rows={3}
                                        value={testIssueBody}
                                        onChange={(e) => setTestIssueBody(e.target.value)}
                                        placeholder="Enter issue description..."
                                    />
                                </div>

                                <button
                                    className="btn btn-outline-black w-full"
                                    onClick={handleCreateTestIssue}
                                    disabled={creatingTest || !testRepo.trim()}
                                >
                                    {creatingTest ? 'Creating...' : 'Create Test Issue'}
                                </button>
                            </div>

                            {/* Disconnect Section */}
                            <div className="border-t pt-4">
                                <h3 className="font-semibold text-font-16 mb-3 text-red-600">Danger Zone</h3>
                                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                                    <p className="text-red-700 text-sm mb-3">
                                        Disconnecting will remove all GitHub integrations and stop all repository automation.
                                    </p>
                                    <button
                                        className="btn btn-outline-red"
                                        onClick={handleDisconnect}
                                        disabled={loading}
                                    >
                                        {loading ? 'Disconnecting...' : 'Disconnect GitHub'}
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

export default GitHubConfigModal; 