import React from 'react';

const BuildSolutionsScreen = () => {
  return (
    <div className="flex flex-col items-center text-center px-4 py-2">
      <div className="mb-4">
        <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center mx-auto mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-blue-600 dark:text-blue-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
        </div>
      </div>
      
      <h2 className="text-xl font-semibold mb-3 text-gray-800 dark:text-white">
        Build Your Own Solutions
      </h2>
      
      <p className="text-gray-600 dark:text-gray-300 mb-4 max-w-lg text-sm">
        Weam AI gives you the flexibility to create custom solutions tailored to your specific needs.
        Build workflows, integrate with your existing tools, and develop domain-specific applications.
      </p>
      
      <div className="grid grid-cols-2 gap-4 w-full max-w-2xl">
        <FeatureCard 
          title="Create Custom Workflows" 
          description="Design and implement workflows tailored to your business processes."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Integrate Existing Tools" 
          description="Connect Weam AI with your current software stack for seamless operations."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Domain-Specific Solutions" 
          description="Build specialized applications for your industry or business domain."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="No-Code/Low-Code Approach" 
          description="Create solutions without extensive coding knowledge using our intuitive interface."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
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

export default BuildSolutionsScreen;