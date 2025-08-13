'use client';

import React from 'react';

const Screen2MultipleLLM = () => {
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
                    Use Multiple LLM Models
                </h2>
                <p className="text-gray-600 mb-6 max-w-md mx-auto text-sm">
                    Access the best AI models in one platform and choose the perfect model for every task.
                </p>
            </div>

            {/* LLM Model Cards */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="flex flex-col items-center p-4 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-gray-600 font-bold text-sm">GPT</span>
                    </div>
                    <span className="text-xs font-medium">OpenAI GPT</span>
                </div>

                <div className="flex flex-col items-center p-4 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-gray-600 font-bold text-sm">C</span>
                    </div>
                    <span className="text-xs font-medium">Claude</span>
                </div>

                <div className="flex flex-col items-center p-4 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-gray-600 font-bold text-sm">G</span>
                    </div>
                    <span className="text-xs font-medium">Gemini</span>
                </div>

                <div className="flex flex-col items-center p-4 bg-white border rounded-lg shadow-sm h-24 justify-between">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                        <span className="text-gray-600 font-bold text-sm">+</span>
                    </div>
                    <span className="text-xs font-medium">More Models</span>
                </div>
            </div>

            {/* Feature Benefits */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Compare Responses</h4>
                        <p className="text-xs text-gray-600">Compare model responses side-by-side</p>
                    </div>
                </div>

                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                        </svg>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Best for Tasks</h4>
                        <p className="text-xs text-gray-600">Choose the best model for specific tasks</p>
                    </div>
                </div>

                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        </svg>
                    </div>
                    <div>
                        <h4 className="font-semibold text-sm mb-1">Switch Seamlessly</h4>
                        <p className="text-xs text-gray-600">Switch between models seamlessly</p>
                    </div>
                </div>

                <div className="flex items-start space-x-3">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mt-1">
                        <svg className="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 100 4m0-4v2m0-6V4" />
                        </svg>
                    </div>
                    <div className="text-left">
                        <h4 className="font-semibold text-sm mb-1">Optimize Performance</h4>
                        <p className="text-xs text-gray-600">Access to various AI models</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Screen2MultipleLLM;
