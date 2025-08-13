'use client';

import { useEffect, useState } from 'react';
import Onboard from '@/components/Initial/Onboard';
import OnboardingFlow from '@/components/Onboarding/OnboardingFlow';
import { getCurrentUser } from '@/utils/handleAuth';
import { redirect } from 'next/navigation';
import routes from '@/utils/routes';

export default function Home() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        // Get current user
        const currentUser = getCurrentUser();
        setUser(currentUser);
        setLoading(false);
        
        // If no user is logged in, redirect to login
        if (!currentUser && !loading) {
            redirect(routes.login);
        }
    }, [loading]);
    
    // If user has onboard flag set to false, redirect to dashboard
    if (user && user.onboard === false) {
        redirect(routes.dashboard);
    }
    
    return (
        <div className="flex h-full flex-col px-5 overflow-y-auto w-full justify-center">
            {user && user.onboard === true ? (
                <OnboardingFlow />
            ) : (
                <Onboard />
            )}
        </div>
    );
}
