'use client';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import CurrentPlan from '@/components/Subscription/CurrentPlan';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { useSubscription } from '@/hooks/subscription/useSubscription';
import { useEffect, useState } from 'react';
import UpcomingInvoice from '@/components/Subscription/UpcomingInvoice';
import ThreeDotLoader from '@/components/Loader/ThreeDotLoader';
import { useSelector, useDispatch } from 'react-redux';
import { setReloadSubscription } from '@/lib/slices/subscription/subscriptionSlice';
import InvoiceList from '@/components/Subscription/InvoiceList';
import { BASIC_AUTH, STRIPE_PUBLISH_KEY, STRIPE_TEST_PRICE_ID } from '@/config/config';
import { SUBSCRIPTION_STATUS } from '@/utils/constant';
import { getCurrentUser } from '@/utils/handleAuth';
import RazorpaySubscriptionForm from '@/components/Subscription/RazorPaySubscriptionForm';
import { useRazorpaySubscription } from '@/hooks/subscription/useRazorpaySubscription';
import RazorpayCurrentPlan from '@/components/Subscription/RazorpayCurrentPlan';
import { useRouter } from 'next/navigation';
import routes from '@/utils/routes';
import TestSubscriptionFormWrapper from '@/components/Subscription/TestStripeSubscriptionForm';

const stripePromise = loadStripe(STRIPE_PUBLISH_KEY);

const TestSubscription = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showAuthPrompt, setShowAuthPrompt] = useState(true);
    const router = useRouter();

    useEffect(() => {
        // Show authentication prompt when component mounts
        if (showAuthPrompt) {
            const usernameInput = prompt('Please enter your username:');
            if (usernameInput== BASIC_AUTH.USERNAME) {
                setUsername(usernameInput);
                const passwordInput = prompt('Please enter your password:');
                if (passwordInput== BASIC_AUTH.PASSWORD) {
                    setPassword(passwordInput);
                    // Simple validation - you can replace this with your actual validation logic
                    if (usernameInput.length > 3 && passwordInput.length > 3) {
                        setIsAuthenticated(true);
                        setShowAuthPrompt(false);
                    } else {
                        alert('Invalid username or password');
                        router.push(routes.login);
                    }
                } else {
                    alert('Authentication required');
                    router.push(routes.login);
                }
            } else {
                alert('Authentication required');
                router.push(routes.login);
            }
        }
    }, [showAuthPrompt, router]);
   
    const {
        subscriptionData,
        loading: subscriptionLoading,
        fetchActiveSubscription,
        cancelSubscription,
        upcomingInvoice,
        upcomingInvoiceData,
        upcomingLoading,
        showDefaultPaymentMethod,
        paymentMethodData,
        unCancelSubscription,
        dataLoading,
    } = useSubscription();

    const {
        fetchRazorpaySubscription,
        loading: razorpayLoading,
        razorpaySubscriptionData,
        cancelRazorpaySubscription,
        getRazorpayPaymentMethod,
        razorpayPaymentMethodData,
        unCancelRazorpaySubscription,
    } = useRazorpaySubscription();

    const user = getCurrentUser();

    const dispatch = useDispatch();
    const reloadSubscription = useSelector((state:any) => state.subscription.reloadSubscription);
    
    useEffect(() => {
        if (!isAuthenticated) return;
        
        if(user?.countryCode == 'IN' && user?.company?.name?.startsWith("Razorpay")){
            fetchRazorpaySubscription()
        }else{
            fetchActiveSubscription(null);        
        }
    }, [isAuthenticated]);

    useEffect(() => {
        if (!isAuthenticated) return;
        
        if(user?.countryCode == 'IN' && user?.company.name.startsWith("Razorpay")){
            fetchRazorpaySubscription()
            dispatch(setReloadSubscription(false));
        }
        else {
            fetchActiveSubscription(null);
            dispatch(setReloadSubscription(false));
        }  
    }, [reloadSubscription, isAuthenticated]);

    if (!isAuthenticated) {
        return <ThreeDotLoader loading={true} />;
    }

    return (
        <div className="flex flex-col flex-1 relative h-full overflow-hidden lg:pt-20 pb-10 px-2">
            <div className="h-full overflow-y-auto w-full relative">
            {(user?.countryCode == 'IN' && user?.company?.name?.startsWith("Razorpay")) ? (
                <div className="mx-auto max-w-[950px]">
                    <Tabs defaultValue="manage-plan" className="w-full">
                        <TabsList className="px-0 space-x-10">
                            <TabsTrigger className="px-0 font-medium" value="manage-plan">
                                Manage Plan
                            </TabsTrigger>
                            <TabsTrigger className="px-0 font-medium" value="manage-invoice">
                                Manage Invoice
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="manage-plan" className="p-0 max-w-[calc(100vw-25px)] overflow-x-auto">
                        {razorpayLoading ? (
                            <ThreeDotLoader loading={razorpayLoading} />
                        ) : razorpaySubscriptionData && Object.keys(razorpaySubscriptionData).length > 0 ? 
                        <>
                            <RazorpayCurrentPlan  
                                subscriptionData={razorpaySubscriptionData} 
                                cancelSubscription={cancelRazorpaySubscription} 
                                showDefaultPaymentMethod={getRazorpayPaymentMethod} 
                                paymentMethodData={razorpayPaymentMethodData}
                                unCancelSubscription={unCancelRazorpaySubscription}
                                dataLoading={razorpayLoading}
                                onRefresh={fetchRazorpaySubscription}
                            />
                            {!subscriptionData?.cancel_at && subscriptionData.subscriptionStatus == SUBSCRIPTION_STATUS.ACTIVE && (
                                <UpcomingInvoice 
                                    subscription={razorpaySubscriptionData} 
                                    upcomingLoading={upcomingLoading} 
                                    upcomingInvoice={upcomingInvoice} 
                                    upcomingInvoiceData={upcomingInvoiceData} 
                                />
                            )}
                        </> :  
                           razorpaySubscriptionData &&<RazorpaySubscriptionForm/>          
                        }
                        </TabsContent>

                        <TabsContent value="manage-invoice" className="p-0">
                            <InvoiceList />
                        </TabsContent>
                    </Tabs>
                </div>
            ) : (
                <div className="mx-auto max-w-[950px]">
                    <Tabs defaultValue="manage-plan" className="w-full">
                        <TabsList className="px-0 space-x-10">
                            <TabsTrigger className="px-0 font-medium" value="manage-plan">
                                Manage Plan
                            </TabsTrigger>
                            <TabsTrigger className="px-0 font-medium" value="manage-invoice">
                                Manage Invoice 
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="manage-plan" className="p-0 max-w-[calc(100vw-25px)] overflow-x-auto">
                        {subscriptionLoading ? (
                            <ThreeDotLoader loading={subscriptionLoading} />
                        ) : subscriptionData && Object.keys(subscriptionData).length > 0 ? 
                        <>
                            <CurrentPlan  
                                subscriptionData={subscriptionData} 
                                cancelSubscription={cancelSubscription} 
                                showDefaultPaymentMethod={showDefaultPaymentMethod} 
                                paymentMethodData={paymentMethodData}
                                unCancelSubscription={unCancelSubscription}
                                dataLoading={dataLoading}                                  
                            />
                            {!subscriptionData?.cancel_at && subscriptionData.subscriptionStatus == SUBSCRIPTION_STATUS.ACTIVE && (
                                <UpcomingInvoice 
                                    subscription={subscriptionData} 
                                    upcomingLoading={upcomingLoading} 
                                    upcomingInvoice={upcomingInvoice} 
                                    upcomingInvoiceData={upcomingInvoiceData} 
                                />
                            )}
                        </> : (
                            <>
                               { subscriptionData && <Elements stripe={stripePromise}>
                                    <TestSubscriptionFormWrapper testPriceId={STRIPE_TEST_PRICE_ID} />
                                </Elements>}
                            </>
                        )}
                        </TabsContent>

                        <TabsContent value="manage-invoice" className="p-0">
                            <InvoiceList />
                        </TabsContent>
                    </Tabs>
                </div>
            )}
            </div>
        </div>
    );
}

export default TestSubscription;