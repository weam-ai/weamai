import React from 'react';
import Image from 'next/image';

const WelcomeScreen = () => {
  return (
    <div className="flex flex-col items-center text-center">
      <div className="mb-6">
        <Image 
          src="/weam-logo.svg" 
          alt="Weam AI Logo" 
          width={120} 
          height={120}
          className="mx-auto"
        />
      </div>
      
      <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
        Welcome to Weam AI
      </h2>
      
      <p className="text-gray-600 dark:text-gray-300 mb-6 max-w-lg">
        We're excited to have you on board! Let's take a few moments to set up your workspace 
        and get you familiar with our platform's key features.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl">
        <FeatureCard 
          title="Smart AI Assistant" 
          description="Get instant help with your tasks using our advanced AI assistant."
          icon="🤖"
        />
        <FeatureCard 
          title="Team Collaboration" 
          description="Work seamlessly with your team members in real-time."
          icon="👥"
        />
        <FeatureCard 
          title="Knowledge Base" 
          description="Access and build your organization's knowledge repository."
          icon="📚"
        />
      </div>
    </div>
  );
};

const FeatureCard = ({ title, description, icon }) => {
  return (
    <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg transition-all hover:shadow-md">
      <div className="text-4xl mb-2">{icon}</div>
      <h3 className="font-medium text-lg mb-2 text-gray-800 dark:text-white">{title}</h3>
      <p className="text-gray-600 dark:text-gray-300 text-sm">{description}</p>
    </div>
  );
};

export default WelcomeScreen;