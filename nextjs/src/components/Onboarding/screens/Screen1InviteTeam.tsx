'use client';

import React from 'react';

const Screen1InviteTeam = () => {
    return (
        <div className="text-center h-full flex flex-col justify-between">
            {/* Weam Logo */}
            <div className="flex justify-center mb-4">
                <div className="text-3xl font-bold">
                    <span className="text-black">Weam</span>
                    <span className="text-blue-500"></span>
                </div>
            </div>

            {/* Main Content */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2 text-gray-800">
                    Invite Your Team Members
                </h2>
                <p className="text-gray-600 mb-6 max-w-md mx-auto text-sm">
                    Collaborate seamlessly with your team members and unlock the full potential of AI-powered teamwork.
                </p>
            </div>

            {/* Feature Cards */}
            <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="flex flex-col items-center p-4 bg-white border rounded-lg shadow-sm h-28 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                    </div>
                    <div className="text-center">
                        <h3 className="font-semibold text-sm mb-1">Share Workspaces</h3>
                        <p className="text-xs text-gray-500">Share workspaces and projects</p>
                    </div>
                </div>

                <div className="flex flex-col items-center p-4 bg-white border rounded-lg shadow-sm h-28 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <div className="text-center">
                        <h3 className="font-semibold text-sm mb-1">Real-time Collaboration</h3>
                        <p className="text-xs text-gray-500">Collaborate in real-time</p>
                    </div>
                </div>

                <div className="flex flex-col items-center p-4 bg-white border rounded-lg shadow-sm h-28 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.031 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                    </div>
                    <div className="text-center">
                        <h3 className="font-semibold text-sm mb-1">Team Permissions</h3>
                        <p className="text-xs text-gray-500">Manage team permissions</p>
                    </div>
                </div>
            </div>

            {/* Additional Benefits */}
            <div className="bg-gray-50 rounded-lg p-5 mb-4">
                <h4 className="font-semibold text-sm mb-3">Why invite your team?</h4>
                <ul className="text-xs text-gray-600 space-y-2">
                    <li>• Streamline team workflows</li>
                    <li>• Share AI insights and solutions</li>
                    <li>• Collaborate on complex projects</li>
                    <li>• Build a knowledge base together</li>
                </ul>
            </div>
        </div>
    );
};

export default Screen1InviteTeam;
