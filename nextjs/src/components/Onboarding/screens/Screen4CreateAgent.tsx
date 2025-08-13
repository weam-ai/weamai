'use client';

import React from 'react';

const Screen4CreateAgent = () => {
    return (
        <div className="text-center h-full flex flex-col justify-between">
            {/* Weam Logo */}
            <div className="flex justify-center mb-4">
                <div className="text-2xl font-bold">
                    <span className="text-black">Weam</span>
                    <span className="text-blue-500">.</span>
                </div>
            </div>

            {/* Main Content */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2 text-gray-800">
                    Create Agents & Prompt Library
                </h2>
                <p className="text-gray-600 mb-6 max-w-md mx-auto text-sm">
                    Build custom AI agents and create a library of prompts for your team.
                </p>
            </div>

            {/* Central Icon */}
            <div className="flex justify-center mb-4">
                <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-12 h-12 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                </div>
            </div>
            <div className="text-sm font-medium mb-6">Your Custom AI Agent</div>

            {/* Feature Cards */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Custom AI Agents</h4>
                        <p className="text-xs text-gray-600">Create specialized AI agents for different tasks</p>
                    </div>
                </div>

                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
                        </svg>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Prompt Library</h4>
                        <p className="text-xs text-gray-600">Build a library of effective prompts</p>
                    </div>
                </div>

                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
                        </svg>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Share Templates</h4>
                        <p className="text-xs text-gray-600">Share agent templates with your team</p>
                    </div>
                </div>

                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Reuse Prompts</h4>
                        <p className="text-xs text-gray-600">Reuse and adapt prompts for efficiency</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Screen4CreateAgent;
