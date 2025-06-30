'use client';
import Script from 'next/script';
import { useEffect } from 'react';
declare global {
    interface Window {
        Razorpay: any;
    }
}

const TestSubscription = () => {
    const handlePayment = async () => {
        // Fetch the subscription ID from your server
        const response = await fetch('http://localhost:4050/api/admin/razorpay/create-razorpay-customer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        const razorPayData = await response.json();
        console.log(razorPayData);
        
        var options = {
            "key": "rzp_test_FTwA7rssDVofnb",
            "order_id": razorPayData?.data?.order?.id,
            "customer_id": razorPayData?.data?.customer?.customerId,
            "recurring": "1",
            "handler": function (response) {
            //   alert(response.razorpay_payment_id);
            //   alert(response.razorpay_order_id);
            //   alert(response.razorpay_signature);
            console.log('response', razorPayData);
                fetchRazorPayToken(response.razorpay_payment_id, razorPayData?.data?.customer?.customerId);
            },
            "notes": {
              "note_key 1": "Beam me up Scotty",
              "note_key 2": "Tea. Earl Gray. Hot."
            },
            "theme": {
              "color": "#F37254"
            }
        };
        
        const rzp = new window.Razorpay(options);
        rzp.open();
    };

    const fetchRazorPayToken = async (paymentId, customerId) => {
        const response = await fetch('http://localhost:4050/api/admin/razorpay/fetch-razorpay-token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                paymentId: paymentId,
                customerId: customerId
            })
        });
        const razorPayData = await response.json();
        //console.log(razorPayData);
    }

    useEffect(() => {
        //alert('fetchRazorPayToken');
        //fetchRazorPayToken('pay_QRFMICDmFVRxQj');
    }, []);
    return (
        <div>
            <Script src="https://checkout.razorpay.com/v1/checkout.js" />
            <h1>Test Subscription</h1>
            <button onClick={handlePayment}>Subscribe Now</button>
        </div>
    );
}

export default TestSubscription;