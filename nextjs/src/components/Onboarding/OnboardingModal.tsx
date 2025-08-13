'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { getCurrentUser, setUserData } from '@/utils/handleAuth';
import axios from 'axios';
import { LINK, NODE_API_PREFIX } from '@/config/config';
import { toast } from 'react-hot-toast';
import routes from '@/utils/routes';

// Import individual screen components
import Screen1InviteTeam from './screens/Screen1InviteTeam';
import Screen2MultipleLLM from './screens/Screen2MultipleLLM';
import Screen3BuildSolutions from './screens/Screen3BuildSolutions';
import Screen4CreateAgent from './screens/Screen4CreateAgent';
import Screen5AIWorld from './screens/Screen5AIWorld';
import commonApi from '@/api';
import { MODULES } from '@/utils/constant';
import { USER } from '@/utils/localstorage';
import { encryptedPersist } from '@/utils/helper';

const OnboardingModal = () => {
    const [open, setOpen] = useState(false);
    const [currentStep, setCurrentStep] = useState(0);
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const user = getCurrentUser();

    useEffect(() => {
        // Show onboarding modal if user has onboard flag set to true
        console.log("user",user)
        if (user && user.onboard === true) {
            setOpen(true);
        } else {
            setOpen(false);
        }
    }, [user]);

    // Define the 5 onboarding screens
    const screens = [
        {
            id: 'invite-team',
            component: <Screen1InviteTeam />,
            title: 'Invite Your Team Members'
        },
        {
            id: 'multiple-llm',
            component: <Screen2MultipleLLM />,
            title: 'Use Multiple LLM Models'
        },
        {
            id: 'build-solutions',
            component: <Screen3BuildSolutions />,
            title: 'Build Your Own Solutions'
        },
        {
            id: 'create-agent',
            component: <Screen4CreateAgent />,
            title: 'Create Your Own Agent & Prompt Library'
        },
        {
            id: 'ai-world',
            component: <Screen5AIWorld />,
            title: 'Be Part of the AI World'
        }
    ];

    const handleNext = () => {
        if (currentStep < screens.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            handleComplete();
        }
    };

    const handleBack = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const handleSkip = async () => {
        await handleComplete();
    };

    const handleComplete = async () => {
        const currentUser= getCurrentUser()
        setLoading(true);
        console.log('currentUser', currentUser)

        try {
            
            console.log('user', `${LINK.COMMON_NODE_API_URL}${NODE_API_PREFIX}/web/auth/complete-onboarding`)
            
            const res = await commonApi({
                action: MODULES.COMPLETE_ONBOARDING,
                data: {
                    userId :currentUser?._id
                },
            })

            if(res.data.success){
                setOpen(false)
                toast.success('Welcome to Weam! Your onboarding is complete.');
            }
            
            
            // Update local user data
                 const userInfo = setUserData(res.data.user);
                       
                       encryptedPersist(userInfo, USER);
            
            // // Close modal first
            // setOpen(false);
            
            // Show success message
            // setTimeout(() => {
            //     toast.success('Welcome to Weam! Your onboarding is complete.');
            // }, 100);
            
            // // Redirect to dashboard
            // setTimeout(() => {
            //     router.push(routes.dashboard);
            // }, 500);
        } catch (error) {
            console.error('Error completing onboarding:', error);
            toast.error('Failed to complete onboarding. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    // Progress calculation
    const progress = ((currentStep + 1) / screens.length) * 100;

    if (!user || user.onboard === false) {
        return null;
    }

    return (
        <Dialog open={open} onOpenChange={() => {}}>
            <DialogContent 
                className="md:max-w-[800px] max-w-[calc(100%-30px)] py-7 border-none max-h-[90vh] overflow-hidden flex flex-col" 
                showCloseButton={false}
            >
                <DialogHeader className="rounded-t-10 px-[30px] pb-5 border-b">
                    <div className="flex justify-between items-center mb-4">
                        <div className="text-sm text-gray-500">
                            STEP {currentStep + 1} OF {screens.length}
                        </div>
                        <div className="text-sm text-gray-500">
                            {Math.round(progress)}%
                        </div>
                    </div>
                    
                    {/* Progress indicator */}
                    <div className="flex justify-center mb-6">
                        {screens.map((_, index) => (
                            <div
                                key={index}
                                className={`w-8 h-8 rounded-full mx-2 flex items-center justify-center text-sm font-medium transition-all duration-300 ${
                                index === currentStep
                                    ? 'bg-blue-500 text-gray-400 border-2 border-blue-500 shadow-lg'
                                    : index < currentStep
                                    ? 'bg-blue-500 text-gray-400 shadow-md'
                                    : 'bg-gray-200 text-gray-400 border border-gray-300 '
                            }`}
                            >
                                {index + 1}
                            </div>
                        ))}
                    </div>
                    
                    <DialogTitle className="font-bold text-2xl flex justify-center text-center">
                        {screens[currentStep].title}
                    </DialogTitle>
                </DialogHeader>

                <div className="px-5 md:px-10 py-8 overflow-hidden flex-1">
                    <div className="h-[500px] w-full overflow-auto flex items-center justify-center">
                        <div className="w-full max-w-[700px] mx-auto">
                            {screens[currentStep].component}
                        </div>
                    </div>
                </div>

                <div className="flex justify-between items-center mt-6 px-5 md:px-10">
                    {/* Back button */}
                    <button
                        type="button"
                        className={`px-6 py-3 btn btn-outline-gray ${
                            currentStep === 0 ? 'invisible' : ''
                        }`}
                        onClick={handleBack}
                        disabled={loading || currentStep === 0}
                    >
                        Back
                    </button>

                    {/* Center buttons */}
                    <div className="flex gap-4">
                        {currentStep < screens.length - 1 ? (
                            <>
                                <button
                                    type="button"
                                    className="px-6 py-3 btn btn-outline-gray"
                                    onClick={handleSkip}
                                    disabled={loading}
                                >
                                    Skip
                                </button>
                                <button
                                    type="button"
                                    className="px-6 py-3 btn btn-blue text-white rounded-md hover:bg-blue-700"
                                    onClick={handleNext}
                                    disabled={loading}
                                >
                                    Next
                                </button>
                            </>
                        ) : (
                            <button
                                type="button"
                                className="px-8 py-3 btn btn-blue text-white rounded-md hover:bg-blue-700"
                                onClick={handleComplete}
                                disabled={loading}
                            >
                                {loading ? 'Completing...' : 'Welcome to Weam'}
                            </button>
                        )}
                    </div>

                    {/* Placeholder for layout balance */}
                    <div className="w-[88px]"></div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default OnboardingModal;
