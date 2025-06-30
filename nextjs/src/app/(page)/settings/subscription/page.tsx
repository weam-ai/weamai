'use client';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import CurrentPlan from '@/components/Subscription/CurrentPlan';
import SubscriptionFormWrapper from '@/components/Subscription/SubscriptionForm';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { useSubscription } from '@/hooks/subscription/useSubscription';
import { useEffect } from 'react';
import UpcomingInvoice from '@/components/Subscription/UpcomingInvoice';
import ThreeDotLoader from '@/components/Loader/ThreeDotLoader';
import { useSelector, useDispatch } from 'react-redux';
import { setReloadSubscription } from '@/lib/slices/subscription/subscriptionSlice';
import InvoiceList from '@/components/Subscription/InvoiceList';
import { STRIPE_PUBLISH_KEY } from '@/config/config';
import { ROLE_TYPE, SUBSCRIPTION_STATUS } from '@/utils/constant';
import { getCurrentUser } from '@/utils/handleAuth';
import RazorpaySubscriptionForm from '@/components/Subscription/RazorPaySubscriptionForm';
import { useRazorpaySubscription } from '@/hooks/subscription/useRazorpaySubscription';
import RazorpayCurrentPlan from '@/components/Subscription/RazorpayCurrentPlan';
const stripePromise = loadStripe(STRIPE_PUBLISH_KEY);

export default function BillingSettings() {
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
    const reloadSubscription = useSelector((state:any) => state.subscription.reloadSubscription); // Get the dispatch state
    
    useEffect(() => {
        if(user?.roleCode == ROLE_TYPE.COMPANY || user?.email == 'pravink@whitelabeliq.com'){
            
        } else {
            window.location.href = '/';
        }

        if(user?.countryCode == 'IN' && user?.company?.name?.startsWith("Razorpay")){
            fetchRazorpaySubscription()
        }else{
            fetchActiveSubscription(null);        
        }
    }, []);

    useEffect(() => {
        if( user?.countryCode == 'IN' && user?.company.name.startsWith("Razorpay")){
            fetchRazorpaySubscription()
            dispatch(setReloadSubscription(false));
        }
        else {
            fetchActiveSubscription(null);
            dispatch(setReloadSubscription(false));
        }
       
    }, [reloadSubscription]);

    return (
        <div className="flex flex-col flex-1 relative h-full overflow-hidden lg:pt-20 pb-10 px-2 max-md:mt-[50px]">
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
                            {/* {!subscriptionData?.cancel_at && subscriptionData.subscriptionStatus == SUBSCRIPTION_STATUS.ACTIVE && (
                                <UpcomingInvoice 
                                    subscription={razorpaySubscriptionData} 
                                    upcomingLoading={upcomingLoading} 
                                    upcomingInvoice={upcomingInvoice} 
                                    upcomingInvoiceData={upcomingInvoiceData} 
                                />
                            )} */}
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
                                    <SubscriptionFormWrapper />
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