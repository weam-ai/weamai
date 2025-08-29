import { LocalStorage } from './localstorage';
import { ONBOARDING_DIALOG_SEEN } from './constant';

/**
 * Onboarding utility functions
 */
export const OnboardingUtils = {
  /**
   * Check if user has seen the onboarding dialog
   */
  hasSeenOnboarding: (): boolean => {
    return !!LocalStorage.get(ONBOARDING_DIALOG_SEEN);
  },

  /**
   * Mark onboarding as seen
   */
  markOnboardingAsSeen: (): void => {
    LocalStorage.set(ONBOARDING_DIALOG_SEEN, 'true');
  },

  /**
   * Reset onboarding state (useful for testing or admin purposes)
   */
  resetOnboarding: (): void => {
    LocalStorage.remove(ONBOARDING_DIALOG_SEEN);
  },

  /**
   * Check if onboarding should be shown
   */
  shouldShowOnboarding: (): boolean => {
    return !OnboardingUtils.hasSeenOnboarding();
  }
};
