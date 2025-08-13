import React from 'react';

const AgentLibraryScreen = () => {
  return (
    <div className="flex flex-col items-center text-center px-3 py-1 onboarding-content">
      <div className="mb-4">
        <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center mx-auto mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-purple-600 dark:text-purple-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
      </div>
      
      <h2 className="text-xl font-semibold mb-3 text-gray-800 dark:text-white">
        Create Your Own Agent & Prompt Library
      </h2>
      
      <p className="text-gray-600 dark:text-gray-300 mb-4 max-w-lg text-sm">
        Build custom AI agents tailored to your specific needs and maintain a library of effective prompts
        to streamline your workflow and enhance productivity.
      </p>
      
      <div className="grid grid-cols-2 gap-3 w-full max-w-2xl">
        <FeatureCard 
          title="Build Custom AI Agents" 
          description="Create specialized AI agents that handle specific tasks for your team."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Save & Organize Prompts" 
          description="Build a library of effective prompts for different use cases and scenarios."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Share Templates with Team" 
          description="Collaborate with your team by sharing your most effective agent configurations and prompts."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Reuse Across Projects" 
          description="Apply your proven prompts and agents across different projects to maintain consistency."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          }
        />
      </div>
    </div>
  );
};

const FeatureCard = ({ title, description, icon }) => {
  return (
    <div className="bg-gray-50 dark:bg-gray-700 p-2 rounded-lg transition-all hover:shadow-md">
      <div className="flex justify-center mb-1">{icon}</div>
      <h3 className="font-medium text-sm mb-0.5 text-gray-800 dark:text-white">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300 text-xs">{description}</p>
    </div>
  );
};

export default AgentLibraryScreen;