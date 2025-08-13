import React from 'react';

const NavigationButtons = ({ 
  currentStep, 
  totalSteps, 
  onNext, 
  onPrevious, 
  onSkip,
  loading,
  isLastScreen = false
}) => {
  // Force-convert currentStep to a number to avoid string comparison issues
  const stepNumber = Number(currentStep);
  const isFirstStep = stepNumber === 0;

  console.log('NavigationButtons - currentStep:', currentStep, 'isFirstStep:', isFirstStep);

  return (
    <div className="flex justify-between items-center">
      {/* Back button */}
      <div className="flex-1">
        {stepNumber > 0 ? (
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              onPrevious();
            }}
            disabled={loading}
            className="px-4 py-1.5 bg-gray-200 dark:bg-gray-600 border border-gray-400 dark:border-gray-500 text-gray-800 dark:text-gray-100 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-colors disabled:opacity-50 font-medium text-sm shadow-sm"
          >
            ← Back
          </button>
        ) : (
          // Empty placeholder to maintain layout
          <div className="w-16"></div>
        )}
      </div>

      {/* Right side buttons */}
      <div className="flex-1 flex justify-end space-x-3">
        {/* Skip button (hidden on last step) */}
        {!isLastScreen && (
          <button
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              console.log('Skip button clicked - calling onSkip function');
              try {
                onSkip();
              } catch (error) {
                console.error('Error in Skip button click handler:', error);
              }
            }}
            disabled={loading}
            className="px-4 py-1.5 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 focus:outline-none focus:underline transition-colors disabled:opacity-50 font-medium text-sm"
          >
            {loading ? 'Skipping...' : 'Skip'}
          </button>
        )}

        {/* Next/Welcome to Weam button */}
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('Next/Welcome button clicked - calling onNext function');
            try {
              onNext();
            } catch (error) {
              console.error('Error in Next/Welcome button click handler:', error);
            }
          }}
          disabled={loading}
          className={`px-4 py-1.5 rounded-md focus:outline-none focus:ring-1 transition-colors disabled:opacity-50 flex items-center font-medium text-sm shadow-sm ${
            isLastScreen 
              ? 'bg-purple-600 text-white hover:bg-purple-700 focus:ring-purple-500' 
              : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
          }`}
        >
          {loading && (
            <svg className="animate-spin -ml-1 mr-2 h-3 w-3 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          )}
          {isLastScreen ? 'Welcome to Weam' : 'Next'}
        </button>
      </div>
    </div>
  );
};

export default NavigationButtons;