'use client';
import React, { useState, useEffect } from 'react';
import { useStripe, CardElement, Elements, useElements } from '@stripe/react-stripe-js';
import { useSubscription } from '@/hooks/subscription/useSubscription';
import { calculateSubscriptionPrice } from '@/utils/helper';
import StorageSelector from '../StorageSelector';
import { loadStripe } from '@stripe/stripe-js';
import { showPrice, showCurrencySymbol, priceId } from '@/utils/common';
import { Member } from '../Users/Member';
import { STRIPE_PUBLISH_KEY, STRIPE_TEST_PRICE_ID } from '@/config/config';
const stripePromise = loadStripe(STRIPE_PUBLISH_KEY);

const TestSubscriptionFormWrapper = ({ isUpdate = false, closeModal, planqty, planPriceId,testPriceId }:any) => {
    return (
        <Elements stripe={stripePromise}>
            <TestSubscriptionForm isUpdate={isUpdate} closeModal={closeModal} planqty={planqty} planPriceId={planPriceId} testPriceId={testPriceId} />
        </Elements>
    );
};

const TestSubscriptionForm = ({ isUpdate = false, closeModal, planqty, planPriceId,testPriceId }) => {

    const [quantity, setQuantity] = useState(planqty || 1);
    const [isLoading, setIsLoading] = useState(false);
    const [couponCode, setCouponCode] = useState(null);
    const [totalMembers, setTotalMembers] = useState(0);
    const [subscriptionPlan, setSubscriptionPlan] = useState(null);
    const [selectedPlan, setSelectedPlan] = useState(null);

    const stripe = useStripe();
    const elements = useElements();

    const {
        testHandleSubscription,
        upgradeSubscription,
        error, setError,
        loading, setLoading,
        getProductPrice,
        productPrice,
        checkCouponCode,
        validCoupon,
        setValidCoupon,
        dataLoading,
        handle3dSubscription
    } = useSubscription();


    useEffect(() => {
        const priceId = STRIPE_TEST_PRICE_ID;
        getProductPrice(priceId);
    }, []);

    const showDiscount = (coupon:any, quantity:any, price:any) => {
        const subTotal = calculateSubscriptionPrice(quantity, price);

        if (coupon.percent_off) {
            const discountAmount = (subTotal * (coupon.percent_off / 100)).toFixed(2); // Calculate discount amount
            return discountAmount;
        } else if (coupon.amount_off && coupon.currency) {
            const discountAmount = (coupon.amount_off / 100).toFixed(2); // Convert cents to dollars
            return discountAmount;
        } else {
            return 0; // Return a default message if no discount is applicable
        }
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setIsLoading(true);
        let result;

        if (isUpdate) {
            const payload = {
                quantity: quantity,
                coupon: couponCode,
                price_id: planPriceId,
                notes: productPrice?.notes
            }

            result = await upgradeSubscription(payload);
            closeModal();
        } else {
            if (!stripe || !elements) {
                return;
            }

            setError(null);

            const { error: stripeError, paymentMethod } = await stripe.createPaymentMethod({
                type: 'card',
                card: elements.getElement(CardElement),
            });

            if (stripeError) {
                setError(stripeError.message);
                return;
            }

            const payload = {
                payment_method: paymentMethod.id,
                coupon: couponCode ? couponCode : null,
                quantity: quantity,
                plan_name: productPrice?.product_name,
                notes: productPrice?.notes
            };
            result = await testHandleSubscription(payload);
            
            // 3. Handle 3D Secure authentication if required
            if (result?.requiresAction === true) {
                const { error: confirmError, paymentIntent } = await stripe.confirmCardPayment(
                    result.subscription.latest_invoice.payment_intent.client_secret
                );

                if (confirmError) {
                    setError(confirmError.message);
                    setIsLoading(false);
                    setLoading(false);
                    return;
                }
                
                if (paymentIntent.status === 'succeeded') {
                    // Toast(SUBSCRIPTION_CREATED_SUCCESSFULLY);
                    result={...result,...payload,price_id:STRIPE_TEST_PRICE_ID}
                    await handle3dSubscription(result)
                }
            }
        }
        setIsLoading(false);
        setLoading(false);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="mb-6 flex justify-between gap-5 flex-col md:flex-row">
                <div className='w-full'>
                    {/* <label className='block text-gray-700 text-sm font-bold mb-2'>Select Plan</label>
                    <div className="space-y-4">
                        {subscriptionPlan?.map((currPlan ,index) => (
                            <div key={currPlan.id} className="flex items-center space-x-3 p-4 border rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                            <input
                                type="radio"
                                id={`${currPlan.id}`}
                                name="plan"
                                value={currPlan.id}
                                className="form-radio h-5 w-5 text-blue-600 focus:ring-blue-500"
                                onChange={() => setSelectedPlan(currPlan)}
                                defaultChecked={index == 0}
                            />
                            <label
                                htmlFor={`${currPlan.id}`}
                                className="text-gray-700 text-sm font-medium cursor-pointer"
                            >
                                {currPlan.item.name}
                            </label>
                            </div>
                        ))}
                    </div> */}


                    <label className="block text-gray-700 text-sm font-bold mb-2">
                        Select User
                    </label>
                    <StorageSelector
                        className="bg-white"
                        min={1}
                        max={500}
                        step={1}
                        initialValue={quantity}
                        unit=""
                        onChange={(newValue) => {
                            setQuantity(newValue);
                        }}
                    />
                    <label className="block text-gray-700 text-sm font-bold mt-5 mb-2">
                        Coupon Code
                    </label>
                    <div className='relative'>
                        <input
                            type="text"
                            value={couponCode}
                            onChange={(e) => setCouponCode(e.target.value)}
                            placeholder="Enter coupon code (optional)"
                            className="w-full border rounded-md p-2 text-gray-700 text-font-14"
                        />
                        {validCoupon && (
                            <button type='button'
                                className='btn btn-red mt-2 mr-2'
                                onClick={() => {
                                    setCouponCode('');
                                    setValidCoupon(null);
                                }}>
                                Remove
                            </button>
                        )}
                        <button type='button' className='btn btn-black h-[39px] sm:absolute mt-2 sm:mt-0 top-0 right-0'
                            onClick={() => checkCouponCode({ coupon: couponCode })}>
                            Check
                        </button>
                    </div>
                </div>

                <div className="sm:min-w-80 bg-b12 px-5 py-3 rounded-md border">
                    <ul>
                        <li className="flex md:items-center items-start justify-between relative mb-2 md:flex-row flex-col">
                            <p className="text-b6 text-font-14">
                                Plan Name :
                            </p>
                            <p className="text-b6 text-font-14 md:ml-2">
                                {dataLoading ? 'NA' : productPrice?.product_name}
                            </p>
                        </li>
                        <li className="flex md:items-center items-start justify-between relative mb-2 md:flex-row flex-col">
                            <p className="text-b6 text-font-14">
                                Plan Price :
                            </p>
                            <p className="text-b6 text-font-14 md:ml-2">
                            {dataLoading ? 'NA' : <>
                                {showCurrencySymbol(productPrice?.currency)}{showPrice(productPrice?.unit_amount)} / {productPrice?.interval} ({productPrice?.unit} Users)
                            </>}
                            </p>
                        </li>
                        <li className="flex md:items-center items-start justify-between relative mb-2 md:flex-row flex-col">
                            <p className="text-b6 text-font-14">
                                Selected Users :
                            </p>
                            <p className="text-b6 text-font-14 md:ml-2">
                                {dataLoading ? 'NA' : `${quantity} Users`}
                            </p>
                        </li>
                        <li className="flex items-center justify-between relative my-3">
                            <hr className='w-full' />
                        </li>
                        <li className="flex items-center justify-between relative font-bold">
                            <p className="text-b3 text-font-14">
                                Sub Total :
                            </p>
                            <p className="text-b3 text-font-14 ml-2">
                                {dataLoading ? 'NA' : <>
                                    {showCurrencySymbol(productPrice?.currency)}{calculateSubscriptionPrice(quantity, productPrice?.unit_amount).toFixed(2)}
                                </>}
                            </p>
                        </li>
                        {validCoupon && (
                            <li className="flex items-center justify-between relative font-bold">
                                <p className="text-b3 text-font-14">
                                    Discount ({validCoupon?.id}) :
                                </p>
                                <p className="text-b3 text-font-14 ml-2">
                                    - {showCurrencySymbol(productPrice?.currency)}{showDiscount(validCoupon, quantity, productPrice?.unit_amount)}
                                </p>
                            </li>
                        )}
                        <li className="flex items-center justify-between relative font-bold">
                            <p className="text-b3 text-font-14">
                                Total :
                            </p>
                            <p className="text-b3 text-font-14 ml-2">
                            {dataLoading ? 'NA' : <>
                                {showCurrencySymbol(productPrice?.currency)}{(
                                    dataLoading ? 0 : (
                                        calculateSubscriptionPrice(
                                            quantity,
                                            productPrice?.unit_amount
                                        ) -
                                        (validCoupon ? parseFloat(showDiscount(validCoupon, quantity, productPrice?.unit_amount) as any) : 0)
                                    ).toFixed(2)
                                )}
                            </>}
                            </p>
                        </li>
                    </ul>
                </div>
            </div>
            <div className={`mb-5 ${totalMembers > quantity ? '' : 'hidden'}`}>
                <b>Please note:</b> Your current member count exceeds the limit of the selected plan. Adjust your member list to proceed.
            </div>
            <div className={`overflow-y-auto max-h-[350px] my-3 user-table`}>
                <Member totalMembers={totalMembers} setTotalMembers={setTotalMembers} />
            </div>
            
            {!isUpdate ? (
                <div className="mb-3">
                    <label className="block text-gray-700 text-sm font-bold mb-2">
                        Card Details
                    </label>
                    <div className="border border-dashed rounded-md p-3">
                        <CardElement
                            options={{
                                style: {
                                    base: {
                                        fontSize: '16px',
                                        color: '#424770',
                                        '::placeholder': {
                                            color: '#aab7c4',
                                        },
                                    },
                                    invalid: {
                                        color: '#9e2146',
                                    },
                                },
                            }}
                        />
                    </div>
                </div>
            ) : ""}

            {error && (
                <p className="text-font-13 font-medium mt-1 text-red">
                    {error}
                </p>
            )}

            <div className="flex justify-center">
            {/* {currentUser?.countryCode == 'IN' ? 
                <button
                    disabled={!stripe || loading || (totalMembers > quantity)}
                    className={`btn btn-blue
                        ${(!stripe || loading || (totalMembers > quantity)) ? 'opacity-50 cursor-not-allowed' : ''}`}
                    onClick={handleRazorpayPayment}
                >
                    {loading ? 'Processing...' : isUpdate ? 'Update Subscription' : 'Subscribe Now'}
                </button> :  */}
                <button
                    type="submit"
                    disabled={!stripe || loading || (totalMembers > quantity)}
                    className={`btn btn-blue
                        ${(!stripe || loading || (totalMembers > quantity)) ? 'opacity-50 cursor-not-allowed' : ''}`}
                   
                >
                    {loading ? 'Processing...' : isUpdate ? 'Update Subscription' : 'Subscribe Now'}
                </button>
                {/* } */}
            </div>
        </form>
    );
};


export default TestSubscriptionFormWrapper;