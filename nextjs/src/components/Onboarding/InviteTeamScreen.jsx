import React, { useState } from 'react';
import { REGEX } from '@/utils/helper';

const InviteTeamScreen = ({ preferences, setPreferences }) => {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  
  // Handle adding a team member
  const handleAddMember = () => {
    // Validate email
    if (!email) {
      setError('Please enter an email address');
      return;
    }
    
    if (!REGEX.EMAIL_FORMAT_REGEX.test(email)) {
      setError('Please enter a valid email address');
      return;
    }
    
    // Check if email already exists in the list
    if (preferences.teamMembers.includes(email)) {
      setError('This email has already been added');
      return;
    }
    
    // Add email to the list
    setPreferences(prev => ({
      ...prev,
      teamMembers: [...prev.teamMembers, email]
    }));
    
    // Clear input and error
    setEmail('');
    setError('');
  };
  
  // Handle removing a team member
  const handleRemoveMember = (emailToRemove) => {
    setPreferences(prev => ({
      ...prev,
      teamMembers: prev.teamMembers.filter(email => email !== emailToRemove)
    }));
  };
  
  // Handle key press (Enter)
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddMember();
    }
  };

  return (
    <div className="flex flex-col space-y-4 w-full max-w-2xl mx-auto onboarding-content">
      <div>
        <h3 className="text-xl font-medium text-gray-800 dark:text-white mb-1">Invite Your Team</h3>
        <p className="text-gray-600 dark:text-gray-300 text-sm">
          Add team members to collaborate with you on Weam AI
        </p>
      </div>
      
      {/* Email input */}
      <div className="space-y-1">
        <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Email Address
        </label>
        <div className="flex">
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="colleague@company.com"
            className="flex-grow px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-l-md focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
          />
          <button
            onClick={handleAddMember}
            className="px-3 py-2 bg-blue-500 text-white rounded-r-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Add
          </button>
        </div>
        {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Enter email addresses of colleagues you'd like to invite
        </p>
      </div>
      
      {/* Team members list */}
      <div className="space-y-2">
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {preferences.teamMembers.length > 0 ? 'Team Members to Invite' : 'No team members added yet'}
        </h4>
        
        <div className="space-y-1">
          {preferences.teamMembers.map((memberEmail, index) => (
            <div 
              key={index} 
              className="flex items-center justify-between bg-gray-50 dark:bg-gray-700 px-3 py-1.5 rounded-md"
            >
              <span className="text-gray-800 dark:text-gray-200">{memberEmail}</span>
              <button
                onClick={() => handleRemoveMember(memberEmail)}
                className="text-gray-500 hover:text-red-500 focus:outline-none"
                aria-label="Remove team member"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      </div>
      
      <div className="pt-2">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          You can always invite more team members later from the dashboard.
        </p>
      </div>
    </div>
  );
};

export default InviteTeamScreen;