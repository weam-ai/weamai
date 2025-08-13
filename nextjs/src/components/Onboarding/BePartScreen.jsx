import React from 'react';

const BePartScreen = () => {
  return (
    <div className="flex flex-col items-center text-center px-4 py-2">
      <div className="mb-4">
        <div className="w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center mx-auto mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-green-600 dark:text-green-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
      </div>
      
      <h2 className="text-xl text-red font-semibold mb-3 text-gray-800 dark:text-white">
        Be Part of the AI World
      </h2>
      
      <p className="text-gray-600 dark:text-gray-300 mb-4 max-w-lg text-sm">
        Join a community of AI innovators and shape the future of artificial intelligence applications.
        Stay updated with the latest developments and access valuable resources.
      </p>
      
      {/* Centered star icon */}
      <div className="flex justify-center mb-4">
        <div className="w-10 h-10 bg-yellow-100 dark:bg-yellow-900 rounded-full flex items-center justify-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-yellow-500" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-4 w-full max-w-2xl">
        <FeatureCard 
          title="AI Community" 
          description="Join a community of AI innovators"
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Latest Updates" 
          description="Stay updated with latest AI developments"
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Resources" 
          description="Access resources and tutorials"
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Shape Future" 
          description="Shape the future of AI applications"
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          }
        />
      </div>
    </div>
  );
};

const FeatureCard = ({ title, description, icon }) => {
  return (
    <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg transition-all hover:shadow-md">
      <div className="flex justify-center mb-2">{icon}</div>
      <h3 className="font-medium text-sm mb-1 text-gray-800 dark:text-white">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300 text-xs">{description}</p>
    </div>
  );
};

export default BePartScreen;