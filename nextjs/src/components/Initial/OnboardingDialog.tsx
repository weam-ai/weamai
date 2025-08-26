'use client';
import React, { useState, useEffect } from 'react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { SessionStorage } from '@/utils/localstorage';
import { ONBOARDING_DIALOG_SEEN } from '@/utils/constant';
import Image from "next/image";
import DialogFooter from './DialogFooter';
import WeamLogo from '../Shared/WeamLogo';
import Close from '@/icons/Close';
import { onboardingSteps } from './OnboardingSteps';

const OnboardingDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const totalSteps = onboardingSteps.length;

  useEffect(() => {
    const hasSeenDialog = SessionStorage.getItem(ONBOARDING_DIALOG_SEEN);
    if (!hasSeenDialog) {
      const timer = setTimeout(() => {
        setIsOpen(true);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, []);

  const closeDialog = () => {
    SessionStorage.setItem(ONBOARDING_DIALOG_SEEN, 'true');
    setIsOpen(false);
  };

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      closeDialog();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const StepContent = onboardingSteps[currentStep];

  if (!isOpen) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogContent
        className="lg:max-w-[900px] overflow-hidden md:max-w-[700px] max-w-[calc(100%-30px)] py-7 border-none bg-[linear-gradient(115deg,#E7F1FF,#FFFFFF)]"
        showCloseButton={false}
        onInteractOutside={(e) => {
          e.preventDefault();
        }}
        onEscapeKeyDown={(e) => {
          e.preventDefault();
        }}
      >
        <DialogHeader className="rounded-t-10 px-[30px] pb-5">
          <DialogTitle className="flex justify-between items-center">
            <WeamLogo width={125} height={50} className={'w-[75px] h-auto'} />
            <button onClick={closeDialog} className="focus:outline-none">
              <Close width={18} height={18} className="w-4 h-auto fill-black" />
            </button>
          </DialogTitle>
        </DialogHeader>
        <div className="px-8 py-4 max-md:h-[calc(100vh-300px)] overflow-y-auto">
          <StepContent />
        </div>
        <DialogFooter
          totalSteps={totalSteps}
          currentStep={currentStep}
          onSkip={closeDialog}
          onNext={handleNext}
          onPrevious={handlePrevious}
        />
      </DialogContent>
    </Dialog>
  );
};

export default OnboardingDialog;
