'use client';

import React from 'react';

const Screen5AIWorld = () => {
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
            <div className="mb-2">
                <h2 className="text-xl font-semibold mb-2 text-gray-800">
                    Be Part of the AI World
                </h2>
                <p className="text-gray-600 mb-2 max-w-md mx-auto text-sm">
                    Join the AI revolution and stay updated with the latest developments.
                </p>
            </div>

            {/* Central Icon */}
            <div className="flex justify-center mb-6">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                    </svg>
                </div>
            </div>

            {/* Feature Cards */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="flex flex-col items-center p-3 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">AI Community</span>
                </div>

                <div className="flex flex-col items-center p-3 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Latest Updates</span>
                </div>

                <div className="flex flex-col items-center p-3 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Resources</span>
                </div>

                <div className="flex flex-col items-center p-3 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Shape Future</span>
                </div>
            </div>

            {/* Welcome Message */}
            <div className="mb-4">
                <h3 className="text-lg font-semibold mb-2 text-gray-800">
                    Welcome to the AI World!
                </h3>
                <p className="text-gray-600 text-sm">
                    You're all set to start your AI journey with us.
                </p>
            </div>
        </div>
    );
};

export default Screen5AIWorld;
