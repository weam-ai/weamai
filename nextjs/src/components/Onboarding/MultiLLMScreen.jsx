import React from 'react';

const MultiLLMScreen = () => {
  return (
    <div className="flex flex-col items-center text-center px-4 py-2">
      <div className="mb-4">
        <div className="w-16 h-16 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center mx-auto mb-3">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-indigo-600 dark:text-indigo-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        </div>
      </div>
      
      <h2 className="text-xl font-semibold mb-3 text-gray-800 dark:text-white">
        Use Multiple LLM Models
      </h2>
      
      <p className="text-gray-600 dark:text-gray-300 mb-4 max-w-lg text-sm">
        Access a variety of cutting-edge AI models all in one place. Compare responses, 
        choose the best model for each task, and switch seamlessly between different AI providers.
      </p>
      
      <div className="grid grid-cols-2 gap-4 w-full max-w-2xl">
        <FeatureCard 
          title="GPT, Claude, Gemini & More" 
          description="Access to leading AI models from OpenAI, Anthropic, Google, and other providers."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Side-by-Side Comparison" 
          description="Compare responses from different models to find the best answer for your needs."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Task-Specific Models" 
          description="Choose the optimal model for each task - coding, writing, analysis, or creative work."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          }
        />
        
        <FeatureCard 
          title="Seamless Switching" 
          description="Switch between models instantly without losing context or conversation history."
          icon={
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
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

export default MultiLLMScreen;