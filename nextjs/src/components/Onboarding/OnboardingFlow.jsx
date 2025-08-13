'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import routes from '@/utils/routes';
import axios from 'axios';
import { Toast } from '@/utils/toast';
import './onboarding.css';
import { getCurrentUser } from '@/utils/handleAuth';
import { USER } from '@/utils/localstorage';
import { encryptedPersist } from '@/utils/helper';

// Onboarding screens
import InviteTeamScreen from './InviteTeamScreen';
import MultiLLMScreen from './MultiLLMScreen';
import BuildSolutionsScreen from './BuildSolutionsScreen';
import AgentLibraryScreen from './AgentLibraryScreen';
import BePartScreen from './BePartScreen';

// Navigation and progress components
import ProgressIndicator from './ProgressIndicator';
import NavigationButtons from './NavigationButtons';

const OnboardingFlow = () => {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [completedSteps, setCompletedSteps] = useState([]);
  
  // Debug current step
  useEffect(() => {
    console.log('Current step:', currentStep);
  }, [currentStep]);
  
  // User preferences state
  const [preferences, setPreferences] = useState({
    theme: 'light',
    notifications: true,
    teamMembers: []
  });

  // Define the screens in the onboarding flow
  const screens = [
    {
      id: 'invite-team',
      component: <InviteTeamScreen 
        preferences={preferences} 
        setPreferences={setPreferences} 
      />,
      title: 'Invite Your Team Members'
    },
    {
      id: 'multi-llm',
      component: <MultiLLMScreen />,
      title: 'Use Multiple LLM Models'
    },
    {
      id: 'build-solutions',
      component: <BuildSolutionsScreen />,
      title: 'Build Your Own Solutions'
    },
    {
      id: 'agent-library',
      component: <AgentLibraryScreen />,
      title: 'Create Your Own Agent & Prompt Library'
    },
    {
      id: 'be-part',
      component: <BePartScreen />,
      title: 'Be Part of the AI World'
    }
  ];

  // Handle next step navigation
  const handleNext = () => {
    if (currentStep < screens.length - 1) {
      // Add current step to completed steps if not already included
      if (!completedSteps.includes(currentStep)) {
        setCompletedSteps([...completedSteps, currentStep]);
      }
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  // Handle previous step navigation
  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  // Skip onboarding and redirect to dashboard
  const handleSkip = async () => {
    console.log('handleSkip function called');
    setLoading(true);
    try {
      console.log('Skip button clicked - starting API call');
      
      // First update local state to close the modal immediately
      const currentUser = getCurrentUser();
      if (currentUser) {
        const updatedUser = {
          ...currentUser,
          onboard: false
        };
        // Update both localStorage and state
        encryptedPersist(updatedUser, USER);
        console.log('Updated user in localStorage - onboard: false');
      }
      
      // Then make the API call in the background
      try {
        console.log('Making API call to complete onboarding');
        
        // Get the current user to ensure we have the latest data
        const currentUser = getCurrentUser();
        console.log('Current user:', currentUser);
        
        // Make the API call using axios which automatically handles cookies
        const response = await axios.post(
          '/api/complete-onboarding',
          {},
          {
            withCredentials: true, // Important for sending cookies
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );
        
        console.log('API response status:', response.status);
        console.log('API response data:', response.data);
        
        // Show success message
        Toast('Onboarding skipped. You can always update your preferences later.', 'info');
        
        // Redirect to dashboard after successful API call
        console.log('Redirecting to dashboard...');
        window.location.href = routes.dashboard;
        
      } catch (error) {
        console.error('API call failed:', error);
        if (error.response) {
          // The request was made and the server responded with a status code
          console.error('Error response data:', error.response.data);
          console.error('Error status:', error.response.status);
          console.error('Error headers:', error.response.headers);
        } else if (error.request) {
          // The request was made but no response was received
          console.error('No response received:', error.request);
        } else {
          // Something happened in setting up the request
          console.error('Error setting up request:', error.message);
        }
        
        // Even if API call fails, show info message and redirect to dashboard
        // since we've updated localStorage
        Toast('Onboarding skipped. You can always update your preferences later.', 'info');
        console.log('API call failed but still redirecting to dashboard...');
        window.location.href = routes.dashboard;
      }
      
    } catch (error) {
      console.error('Error in handleSkip:', error);
      Toast('Failed to skip onboarding. Please try again.', 'error');
      setLoading(false);
    }
  };

  // Complete onboarding and redirect to dashboard
  const handleComplete = async () => {
    console.log('handleComplete function called');
    setLoading(true);
    try {
      console.log('Welcome to Weam button clicked - starting API call');
      
      // First update local state to close the modal immediately
      const currentUser = getCurrentUser();
      if (currentUser) {
        const updatedUser = {
          ...currentUser,
          onboard: false
        };
        // Update both localStorage and state
        encryptedPersist(updatedUser, USER);
        console.log('Updated user in localStorage - onboard: false');
      }
      
      // Then make the API call in the background
      try {
        console.log('Making API call to complete onboarding');
        
        // Get the current user to ensure we have the latest data
        const currentUser = getCurrentUser();
        console.log('Current user:', currentUser);
        
        // Make the API call using axios which automatically handles cookies
        const response = await axios.post(
          '/api/complete-onboarding',
          {},
          {
            withCredentials: true, // Important for sending cookies
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            }
          }
        );
        
        console.log('API response status:', response.status);
        console.log('API response data:', response.data);
        
        // Show success message
        Toast('Welcome to Weam! Onboarding completed successfully!', 'success');
        
        // Redirect to dashboard after successful API call
        console.log('Redirecting to dashboard...');
        window.location.href = routes.dashboard;
        
      } catch (error) {
        console.error('API call failed:', error);
        if (error.response) {
          // The request was made and the server responded with a status code
          console.error('Error response data:', error.response.data);
          console.error('Error status:', error.response.status);
          console.error('Error headers:', error.response.headers);
        } else if (error.request) {
          // The request was made but no response was received
          console.error('No response received:', error.request);
        } else {
          // Something happened in setting up the request
          console.error('Error setting up request:', error.message);
        }
        
        // Even if API call fails, show success message and redirect to dashboard
        // since we've updated localStorage
        Toast('Welcome to Weam! Onboarding completed.', 'success');
        console.log('API call failed but still redirecting to dashboard...');
        window.location.href = routes.dashboard;
      }
      
    } catch (error) {
      console.error('Error in handleComplete:', error);
      Toast('Failed to complete onboarding. Please try again.', 'error');
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center w-full min-h-screen p-3 bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-4xl bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden flex flex-col h-auto max-h-[90vh]">
        {/* Progress indicator */}
        <div className="p-3 pb-2">
          <ProgressIndicator 
            steps={screens.length} 
            currentStep={currentStep}
            completedSteps={completedSteps}
          />
        </div>
        
        {/* Screen title */}
        <div className="px-4 pb-1">
          <h1 className="text-xl font-bold text-center text-gray-800 dark:text-white">
            {screens[currentStep].title}
          </h1>
        </div>
        
        {/* Screen content - with fixed height and scrollable if needed */}
        <div className="px-2 overflow-y-auto custom-scrollbar" style={{ height: 'auto', maxHeight: 'calc(65vh - 140px)', minHeight: '180px' }}>
          <div className="w-full py-1 onboarding-content">
            {screens[currentStep].component}
          </div>
        </div>
        
        {/* Navigation buttons - fixed at bottom */}
        <div className="p-3 border-t border-gray-200 dark:border-gray-700 mt-auto">
          {/* Debug info */}
          <div className="mb-1 text-xs text-gray-500">
            <span className="hidden">Current step: {currentStep}</span>
          </div>
          
          <NavigationButtons 
            currentStep={currentStep} 
            totalSteps={screens.length} 
            onNext={handleNext} 
            onPrevious={handlePrevious} 
            onSkip={handleSkip} 
            loading={loading}
            isLastScreen={currentStep === screens.length - 1}
          />
        </div>
      </div>
    </div>
  );
};

export default OnboardingFlow;