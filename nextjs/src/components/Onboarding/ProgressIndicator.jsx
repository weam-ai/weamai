import React from 'react';

const ProgressIndicator = ({ steps, currentStep, completedSteps = [] }) => {
  return (
    <div className="w-full max-w-md mx-auto mb-8">
      {/* Progress bar */}
      <div className="relative pt-1">
        <div className="flex mb-2 items-center justify-between">
          <div>
            <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-blue-600 bg-blue-200">
              Step {currentStep + 1} of {steps}
            </span>
          </div>
          <div className="text-right">
            <span className="text-xs font-semibold inline-block text-blue-600">
              {Math.round(((currentStep + 1) / steps) * 100)}%
            </span>
          </div>
        </div>
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-blue-200">
          <div
            style={{ width: `${((currentStep + 1) / steps) * 100}%` }}
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-blue-500 transition-all duration-500 ease-in-out"
          ></div>
        </div>
      </div>

      {/* Step indicators */}
      <div className="flex justify-between items-center w-full">
        {Array.from({ length: steps }).map((_, index) => {
          // Determine if step is active, completed, or upcoming
          const isCompleted = completedSteps.includes(index) || index < currentStep;
          const isActive = index === currentStep;
          const isUpcoming = index > currentStep && !completedSteps.includes(index);

          return (
            <div key={index} className="flex flex-col items-center">
              <div
                className={`
                  flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm border-2
                  ${isCompleted ? 'bg-blue-500 text-white border-blue-500' : ''}
                  ${isActive ? 'bg-blue-600 text-white border-blue-600 ring-2 ring-blue-300' : ''}
                  ${isUpcoming ? 'bg-gray-300 text-gray-700 border-gray-300 dark:bg-gray-600 dark:text-gray-200 dark:border-gray-600' : ''}
                  transition-all duration-200
                `}
              >
                {isCompleted ? (
                  <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                  </svg>
                ) : (
                  <span className="text-center font-bold">
                    {index + 1}
                  </span>
                )}
              </div>
              {index < steps - 1 && (
                <div 
                  className={`
                    hidden sm:block h-0.5 w-full min-w-[3rem] max-w-[5rem] 
                    ${index < currentStep || completedSteps.includes(index) ? 'bg-blue-500' : 'bg-gray-200 dark:bg-gray-700'}
                  `}
                ></div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressIndicator;