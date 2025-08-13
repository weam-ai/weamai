import React from 'react';

const PersonalizeScreen = ({ preferences, setPreferences }) => {
  // Handle theme change
  const handleThemeChange = (theme) => {
    setPreferences(prev => ({
      ...prev,
      theme
    }));
  };

  // Handle notification preferences
  const handleNotificationChange = (e) => {
    setPreferences(prev => ({
      ...prev,
      notifications: e.target.checked
    }));
  };

  return (
    <div className="flex flex-col space-y-8 w-full max-w-2xl mx-auto">
      {/* Theme Selection */}
      <div className="space-y-4">
        <h3 className="text-xl font-medium text-gray-800 dark:text-white">Choose Your Theme</h3>
        <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
          Select a theme that suits your working style
        </p>
        
        <div className="flex flex-wrap gap-4 justify-center">
          <ThemeOption 
            name="Light" 
            value="light" 
            selected={preferences.theme === 'light'}
            onClick={() => handleThemeChange('light')}
            preview="bg-white border border-gray-200"
          />
          
          <ThemeOption 
            name="Dark" 
            value="dark" 
            selected={preferences.theme === 'dark'}
            onClick={() => handleThemeChange('dark')}
            preview="bg-gray-800 border border-gray-700"
          />
          
          <ThemeOption 
            name="System" 
            value="system" 
            selected={preferences.theme === 'system'}
            onClick={() => handleThemeChange('system')}
            preview="bg-gradient-to-r from-white to-gray-800 border border-gray-300"
          />
        </div>
      </div>

      {/* Notification Preferences */}
      <div className="space-y-4">
        <h3 className="text-xl font-medium text-gray-800 dark:text-white">Notification Preferences</h3>
        <p className="text-gray-600 dark:text-gray-300 text-sm mb-4">
          Configure how you'd like to receive updates
        </p>
        
        <div className="flex items-center space-x-3">
          <label className="flex items-center cursor-pointer">
            <div className="relative">
              <input 
                type="checkbox" 
                className="sr-only" 
                checked={preferences.notifications}
                onChange={handleNotificationChange}
              />
              <div className={`block w-14 h-8 rounded-full ${preferences.notifications ? 'bg-blue-500' : 'bg-gray-300 dark:bg-gray-600'}`}></div>
              <div className={`dot absolute left-1 top-1 bg-white w-6 h-6 rounded-full transition-transform ${preferences.notifications ? 'transform translate-x-6' : ''}`}></div>
            </div>
            <div className="ml-3 text-gray-700 dark:text-gray-300 font-medium">
              Enable Notifications
            </div>
          </label>
        </div>
        
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
          You'll receive notifications about team activity, updates, and important alerts
        </p>
      </div>
    </div>
  );
};

const ThemeOption = ({ name, value, selected, onClick, preview }) => {
  return (
    <div 
      className={`flex flex-col items-center space-y-2 cursor-pointer transition-all ${selected ? 'scale-105' : 'opacity-70 hover:opacity-100'}`}
      onClick={onClick}
    >
      <div className={`w-24 h-16 rounded-lg ${preview} shadow-sm`}></div>
      <div className="flex items-center space-x-2">
        <div className={`w-4 h-4 rounded-full border-2 ${selected ? 'border-blue-500 bg-blue-500' : 'border-gray-300 dark:border-gray-600'}`}></div>
        <span className={`text-sm ${selected ? 'font-medium text-blue-500' : 'text-gray-600 dark:text-gray-400'}`}>{name}</span>
      </div>
    </div>
  );
};

export default PersonalizeScreen;