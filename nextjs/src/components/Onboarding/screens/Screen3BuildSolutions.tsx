'use client';

import React from 'react';

const Screen3BuildSolutions = () => {
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
                    Build Solutions
                </h2>
                <p className="text-gray-600 mb-4 max-w-md mx-auto text-sm">
                    Create custom workflows and solutions tailored to your specific needs.
                </p>
            </div>

            {/* Visual Workflow Representation */}
            <div className="flex justify-center items-center mb-6 relative">
                <div className="flex flex-col items-center mx-4">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-2">
                        <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Input</span>
                </div>

                <div className="w-12 h-1 bg-gray-300 mx-2"></div>

                <div className="flex flex-col items-center mx-4">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-2">
                        <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Process</span>
                </div>

                <div className="w-12 h-1 bg-gray-300 mx-2"></div>

                <div className="flex flex-col items-center mx-4">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-2">
                        <svg className="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Output</span>
                </div>
            </div>

            {/* Key Features */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="flex flex-col items-center p-3 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Custom Workflows</span>
                </div>

                <div className="flex flex-col items-center p-3 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Tool Integration</span>
                </div>

                <div className="flex flex-col items-center p-3 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">Domain Solutions</span>
                </div>

                <div className="flex flex-col items-center p-3 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                        </svg>
                    </div>
                    <span className="text-xs font-medium">No-Code Approach</span>
                </div>
            </div>
        </div>
    );
};

export default Screen3BuildSolutions;
