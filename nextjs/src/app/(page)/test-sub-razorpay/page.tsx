'use client';
import { getAccessToken } from '@/actions/serverApi';
import { LINK, RAZORPAY } from '@/config/config';
import { useRazorpaySubscription } from '@/hooks/subscription/useRazorpaySubscription';
import Script from 'next/script';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import routes from '@/utils/routes';
import { BASIC_AUTH } from '@/config/config';

const TestSubscription = () => {

    const [token, setToken] = useState<string | null>(null);
    const handlePayment = async () => {
        const token = await getAccessToken();
        setToken(token);
        // Fetch the subscription ID from your server
        const response = await fetch(
            `${LINK.NODE_API_URL}/api/admin/razorpay/create-razorpay-customer`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `jwt ${token}`,
                },
            }
        );
        const razorPayData = await response.json();
        console.log(razorPayData);
        
        // Store customer ID for later use
        console.log("🚀 ~ handlePayment ~ razorPayData?.data?.customer?.customerId:", razorPayData?.data?.customer?.customerId)
        if (razorPayData?.data?.customer?.customerId) {
            //store this in local storage
            localStorage.setItem('customerId', razorPayData.data.customer.customerId);
        }

        const options = {
            key: RAZORPAY.KEY_ID,
            order_id: razorPayData?.data?.order?.id,
            customer_id: razorPayData?.data?.customer?.customerId,
            recurring: '1',
            handler: function (response) {
                //   alert(response.razorpay_payment_id);
                //   alert(response.razorpay_order_id);
                //   alert(response.razorpay_signature);
                console.log('response', razorPayData);
                fetchRazorPayToken(
                    response.razorpay_payment_id,
                    razorPayData?.data?.customer?.customerId
                );
            },
            theme: {
                color: '#6637EC',
            },
        };
        console.log("🚀 ~ handlePayment ~ options:", options)

        const rzp = new window.Razorpay(options);
        rzp.open();
    };

    const fetchRazorPayToken = async (paymentId, customerId) => {
        const token = await getAccessToken();
        setToken(token);
        const response = await fetch(
            `${LINK.NODE_API_URL}/api/admin/razorpay/fetch-razorpay-token`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `jwt ${token}`,
                },
                body: JSON.stringify({
                    paymentId: paymentId,
                    customerId: customerId,
                }),
            }
        );
        const razorPayData = await response.json();
        console.log(razorPayData);
    };

    const updateSubscription = async () => {
        // const {olderQuantity, newQuantity, oldPlanName, subscriptionStartDate, subscriptionEndDate, newPlanAmount} = req.body;
        const response = await fetch(
            `${LINK.NODE_API_URL}/api/admin/razorpay/update-subscription-demo`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    olderQuantity: 20,
                    newQuantity: 15,
                    oldPlanName: 'LITE',
                    subscriptionStartDate: '2025-04-17T09:14:52.000Z',
                    subscriptionEndDate: '2025-05-17T18:30:00.000Z',
                    newPlanName: 'LITE',
                    tokenId: 'token_QU01Mq6k9egv0R',
                }),
            }
        );
        const razorPayData = await response.json();
        console.log('🚀 ~ updateSubscription ~ razorPayData:', razorPayData);
    };

    const { updateRazorpayCard } =
        useRazorpaySubscription();


    // const handleUpdateCard = async () => {
    //     try {
    //         // For demo purposes - you should get this from your API response
    //         const demoCustomerId = localStorage.getItem('customerId') || "cust_QREmXpzoTpJMvZ"; 
    //         console.log("🚀 ~ handleUpdateCard ~ demoCustomerId:", demoCustomerId)
            
    //         const options = {
    //             key: RAZORPAY.KEY_ID,
    //             // subscription_id: `${subscriptionData.id}`,
    //             customer_id: demoCustomerId,
    //             amount: 100, // 1 rupee = 100 paise (for card verification)
    //             currency: 'INR',
    //             name: 'Weam',
    //             description: 'Card Verification - ₹1 will be auto-refunded',
    //             method: {
    //                 netbanking: false,
    //                 card: true,
    //                 upi: false,
    //                 wallet: false,
    //             },
    //             config: {
    //                 display: {
    //                     blocks: {
    //                         cards: {
    //                             name: 'Credit/Debit Cards',
    //                             instruments: [
    //                                 {
    //                                     method: 'card',
    //                                 },
    //                             ],
    //                         },
    //                     },
    //                     hide: [
    //                         { method: 'netbanking' },
    //                         { method: 'paylater' },
    //                         { method: 'emi' },
    //                         { method: 'wallet' },
    //                         { method: 'upi' },
    //                     ],
    //                     sequence: ['card'],
    //                     preferences: {
    //                         show_default_blocks: false,
    //                     },
    //                 },
    //             },
    //             // Card verification and auto-refund configuration
    //             save: 1, // Save card for future use
    //             subscription_card_change: 1, // Enables updating payment method
    //             recurring: 1, // Enable for subscription/recurring payments
    //             handler: async function (response) {
    //                 console.log('Card verification response:', response);
    //                 if (response?.razorpay_payment_id) {
    //                     try {
    //                         // Update the card information
    //                         const responsea = await updateRazorpayCard({
    //                             payment_id: response?.razorpay_payment_id,
    //                             // subscription_id: subscriptionData?.id,
    //                             payment_method: 'card',
    //                             verification_amount: 100, // 1 rupee for verification
    //                         });
    //                         console.log('🚀 ~ Card updated successfully:', responsea);
                            
    //                         // The ₹1 charge will be automatically refunded by Razorpay within 5-7 business days
    //                         alert('Card verification successful! ₹1 will be refunded within 5-7 business days.');
    //                     } catch (error) {
    //                         console.error('Error updating card:', error);
    //                         alert('Card verification failed. Please try again.');
    //                     }
    //                 }
    //             },
    //             theme: { color: '#6737ec' },
    //         };

    //         const rzp1 = new (window as any).Razorpay(options as any);
    //         rzp1.open();
    //     } catch (error) {
    //         console.error('Error updating card:', error);
    //     }
    // };

    // Alternative method for card verification with auto-refund
    
    const handleCardVerificationWithRefund = async () => {
        try {
            const token = await getAccessToken();
            const demoCustomerId = localStorage.getItem('customerId') || "cust_QREmXpzoTpJMvZ"; 
            console.log("🚀 ~ handleCardVerificationWithRefund ~ demoCustomerId:", demoCustomerId)
            // Create a verification order on your backend
            const response = await fetch(
                `${LINK.NODE_API_URL}/api/admin/razorpay/create-verification-order`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `jwt ${token}`,
                    },
                    body: JSON.stringify({
                        amount: 100, // 1 rupee in paise
                        currency: 'INR',
                        customer_id: demoCustomerId,
                        verification: true, // Flag to indicate this is for verification
                    }),
                }
            );
            
            const orderData = await response.json();
            console.log("🚀 ~ handleCardVerificationWithRefund ~ orderData:", orderData)
            
            const options = {
                key: RAZORPAY.KEY_ID,
                order_id: orderData?.data?.order?.id,
                amount: 100,
                currency: 'INR',
                name: 'Weam',
                description: 'Card Verification - ₹1 (Auto-refundable)',
                method: {
                    card: true,
                    netbanking: false,
                    wallet: false,
                    upi: false,
                },
                handler: async function (response) {
                    console.log('Verification payment response:', response);
                    
                    // Verify the payment and trigger auto-refund
                    const verifyResponse = await fetch(
                        `${LINK.NODE_API_URL}/api/admin/razorpay/verify-and-refund`,
                        {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                Authorization: `jwt ${token}`,
                            },
                            body: JSON.stringify({
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_order_id: orderData?.data?.order?.id,
                                signature: response.razorpay_signature,
                                auto_refund: true, // This will trigger immediate refund
                            }),
                        }
                    );
                    
                    const verifyData = await verifyResponse.json();
                    console.log('Verification and refund response:', verifyData);
                    
                    if (verifyData.status === 200) {
                        alert('Card verified successfully! ₹1 has been refunded immediately.');
                    } else {
                        alert('Card verification failed. Please try again.');
                    }
                },
                customer_id: demoCustomerId,
                theme: { color: '#6737ec' },
                recurring: '1',
                save_card: '1',
                subscription_card_change: '1',
            };

            const rzp = new (window as any).Razorpay(options);
            rzp.open();
        } catch (error) {
            console.error('Error in card verification:', error);
            alert('Card verification failed. Please try again.');
        }
    };

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

    return (
        <div>
            <Script src="https://checkout.razorpay.com/v1/checkout.js" />
            <h1 className='text-font-30 font-bold text-center'>Test Subscription</h1>
            <button onClick={handlePayment} className='bg-blue-500 text-black px-4 py-2 rounded-md cursor-pointer'>Subscribe Now</button>
            <hr />
            <button onClick={updateSubscription} className='bg-blue-500 text-black px-4 py-2 rounded-md cursor-pointer'>Update Subscription</button>
            <hr />
            <button onClick={handleCardVerificationWithRefund} className='bg-blue-500 text-black px-4 py-2 rounded-md cursor-pointer'>Card Verification (₹1 Auto-Refund)</button>
        </div>
    );
};

export default TestSubscription;
