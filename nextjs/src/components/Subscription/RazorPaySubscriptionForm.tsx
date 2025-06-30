import React, { useState, useEffect } from 'react';
import { Member } from '../Users/Member';
import { useRazorpaySubscription } from '@/hooks/subscription/useRazorpaySubscription';
import { RAZORPAY } from '@/config/config';
import StorageSelector from '../StorageSelector';
import Toast from '@/utils/toast';
import { getCurrentUser } from '@/utils/handleAuth';
import { SUBSCRIPTION_CREATED_SUCCESSFULLY } from '@/utils/constant';
import ThreeDotLoader from '@/components/Loader/ThreeDotLoader';
import { useDispatch } from 'react-redux';
import RazorpaySubscriptionOptions from '@/types/subscription';
import { showCurrencySymbol } from '@/utils/common';

type RazorpaySubscriptionFormProps = {
  isUpdate?: boolean;
  closeModal?: () => void;
  planqty?: number;
  planName?: string;
}

const RazorpaySubscriptionForm: React.FC<RazorpaySubscriptionFormProps> = ({
    isUpdate = false,
    closeModal,
    planqty,
    planName
}:RazorpaySubscriptionFormProps) => {
    const [totalMembers, setTotalMembers] = useState(0);
    const [quantity, setQuantity] = useState(planqty || 1);
    const [couponCode, setCouponCode] = useState(null);
    const [subscriptionPlan, setSubscriptionPlan] = useState(null);
    const [selectedPlan, setSelectedPlan] = useState(null);
    const dispatch = useDispatch();
    const {
        fetchRazorpayPlan,
        createRazorpaySubscription,
        loading,
        validCoupon,
        setValidCoupon,
        verifyRazorpayPayment,
        updateRazorpaySubscription
    } = useRazorpaySubscription();
    const currentUser = getCurrentUser();

    const showRazorpayPlan = async () => {
        const plan = await fetchRazorpayPlan();
        console.log("🚀 ~ showRazorpayPlan ~ plan:", plan)
        setSubscriptionPlan(plan.items);
        setSelectedPlan(plan.items[0])
    }

    useEffect(() => {
        showRazorpayPlan();

        // Dynamically load Razorpay script
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        document.body.appendChild(script);
        return () => {
            document.body.removeChild(script);
        };
    }, []);
    
    const handleRazorpayPayment = async () => {
        try {
            
            if(isUpdate){
                const payload = {
                    quantity: quantity,
                    coupon: couponCode,
                    planId: selectedPlan?.id,
                    planName: selectedPlan?.item?.name,
                    planAmount: selectedPlan?.item?.unit_amount,
                    notes: selectedPlan?.notes
                }
                const result = await updateRazorpaySubscription(payload);

                if(result?.status === 200){
                    Toast("Updated Subscription Successfully");          
                    closeModal();
                }
            }
            else{
            // First create subscription
            const subscriptionPayload = {
                amount: selectedPlan?.item?.amount,
                currency: selectedPlan?.item.currency || 'INR',
                quantity: quantity,
                company_id: currentUser?.company.id,
                user_id: currentUser?.id,
                plan_id: selectedPlan?.id,
                coupon: couponCode,
                credit: 0,
                notes: selectedPlan?.notes
            }

            const subscription = await createRazorpaySubscription(subscriptionPayload);
            
            if (!subscription?.data?.id) {
                return;
            }

            const options:any = {
                key: RAZORPAY.KEY_ID,
                subscription_id: subscription.data.id,
                name: 'Weam',
                description: 'Subscription Create Payment',
                offer_id: subscription.data.offer_id,
                save: true,
                handler: async function (response) {
                    try {
                        if (response.razorpay_payment_id) {
                            const verifyPayment = await verifyRazorpayPayment({
                                ...response,
                                type: 'subscription',
                                planId: selectedPlan?.id,
                                quantity,
                                notes: selectedPlan?.notes
                            });
                        }
                       
                        Toast(SUBSCRIPTION_CREATED_SUCCESSFULLY);
                    } catch (error) {
                        console.error('Error processing payment:', error);
                        Toast('An error occurred while processing the payment.');
                    }
                },
                prefill: {
                    name: currentUser?.fname + ' ' + currentUser?.lname,
                    email: currentUser?.email,
                },
                theme: { color: '#6737ec' },
                method: {
                    netbanking: false,
                    card: true,
                    upi: true,
                    wallet: false,
                },
                config: {
                    display: {
                        blocks: {
                            banks: {
                                name: 'Bank Accounts',
                                instruments: [
                                    {
                                        method: 'netbanking'
                                    }
                                ]
                            }
                        },
                        hide: [
                            { method: 'netbanking' },
                            { method: 'paylater' },
                            { method: 'emi' },
                            { method: 'wallet' },
                        ],
                        sequence: ['card',"upi"],
                        preferences: {
                            show_default_blocks: false
                        }
                    }
                }
            };
            const rzp1 = new (window as any).Razorpay(options as RazorpaySubscriptionOptions);
            rzp1.open();
        }

        } catch (error) {
            console.error('Error creating subscription:', error);
            Toast('An error occurred while setting up the subscription.');
        }
    };

    return (
        <form>
            <div className="mb-6 flex justify-between gap-5 flex-col md:flex-row">
                <div className='w-full'>
                    <label className='block text-gray-700 text-sm font-bold mb-2'>Select Plan</label>
                    <div className="space-y-4">
                        {loading ? <ThreeDotLoader /> : subscriptionPlan?.map((currentPlan , index) => (
                            <div key={currentPlan.id} className="flex items-center space-x-3 p-4 border rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                                <input
                                    type="radio"
                                    id={`plan-${currentPlan.id}`}
                                    name="plan"
                                    value={currentPlan.id}
                                    className="form-radio h-5 w-5 text-blue-600 focus:ring-blue-500"
                                    onChange={() => setSelectedPlan(currentPlan)}
                                    defaultChecked={index == 0}
                                />
                                <label
                                    htmlFor={`plan-${currentPlan.id}`}
                                    className="text-gray-700 text-sm font-medium cursor-pointer"
                                >
                                    {currentPlan?.item?.name}
                                </label>
                            </div>
                        ))}
                    </div>
                    <label className="block text-gray-700 text-sm font-bold mb-2 mt-2">
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
                            onChange={(e) => {
                                const value = e.target.value.slice(0, 20);
                                setCouponCode(value);
                            }}
                            maxLength={20}
                            placeholder="Enter coupon code (optional)"
                            className={`w-full border rounded-md p-2 text-gray-700 text-font-14 ${
                                couponCode && couponCode.length !== 20 ? 'border-red-500' : ''
                            }`}
                        />
                        {/* {couponCode && couponCode.length !== 20 && (
                            <p className="text-red-500 text-sm mt-1">
                                Coupon code must be exactly 20 characters
                            </p>
                        )} */}
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
                        {/* <button type='button' className='btn btn-black h-[39px] sm:absolute mt-2 sm:mt-0 top-0 right-0'
                            onClick={() => checkCouponCode({ coupon: couponCode })}>
                            Check
                        </button> */}
                    </div>
                </div>

                <div className="sm:min-w-80 bg-b12 px-5 py-3 rounded-md border">
                   { loading ? <ThreeDotLoader loading={loading} /> : <ul>
                        <li className="flex md:items-center items-start justify-between relative mb-2 md:flex-row flex-col">
                            <p className="text-b6 text-font-14">
                                Plan Name :
                            </p>
                            <p className="text-b6 text-font-14 md:ml-2">
                                {loading ? 'NA' : selectedPlan?.item?.name}
                            </p>
                        </li>
                        <li className="flex md:items-center items-start justify-between relative mb-2 md:flex-row flex-col">
                            <p className="text-b6 text-font-14">
                                Plan Price :
                            </p>
                            <p className="text-b6 text-font-14 md:ml-2">
                                {loading ? 'NA' : `${showCurrencySymbol(selectedPlan?.item?.currency)}${selectedPlan?.item?.unit_amount/100} / User`}
                            </p>
                        </li>
                        <li className="flex md:items-center items-start justify-between relative mb-2 md:flex-row flex-col">
                            <p className="text-b6 text-font-14">
                                Selected Users :
                            </p>
                            <p className="text-b6 text-font-14 md:ml-2">
                                {loading ? 'NA' : quantity}
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
                                {loading ? 'NA' : `${showCurrencySymbol(selectedPlan?.item?.currency)}${selectedPlan?.item?.unit_amount/100 * quantity}`}
                            </p>
                        </li>
                        {/* {discount && ( */}
                            <li className="flex items-center justify-between relative font-bold">
                                <p className="text-b3 text-font-14">
                                    Discount :
                                </p>
                                <p className="text-b3 text-font-14 ml-2">
                                   { `- ${showCurrencySymbol(selectedPlan?.item?.currency)}${(selectedPlan?.item?.discount || 0)/100}`}
                                </p>
                            </li>
                        {/* )} */}
                        <li className="flex items-center justify-between relative font-bold">
                            <p className="text-b3 text-font-14">
                                Total :
                            </p>
                            <p className="text-b3 text-font-14 ml-2">
                                {loading ? 'NA' : `${showCurrencySymbol(selectedPlan?.item?.currency)}${selectedPlan?.item?.unit_amount/100 * quantity - (selectedPlan?.item?.discount || 0)/100}`}
                            </p>
                        </li>
                    </ul>}
                </div>
            </div>

            <div className={`mb-5 ${totalMembers > quantity ? '' : 'hidden'}`}>
                <b>Please note:</b> Your current member count exceeds the limit of the selected plan. Adjust your member list to proceed.
            </div>

            <div className="overflow-y-auto max-h-[350px] my-3 user-table">
                <Member totalMembers={totalMembers} setTotalMembers={setTotalMembers} />
            </div>

            {/* <div className="mb-3">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                    Card Details
                </label>
                <div className="border border-dashed rounded-md p-3">
                    <input
                        type="text"
                        placeholder="Card number"
                        className="w-full mb-2 p-2 border rounded"
                    />
                    <div className="flex gap-4">
                        <input
                            type="text"
                            placeholder="MM/YY"
                            className="w-1/2 p-2 border rounded"
                        />
                        <input
                            type="text"
                            placeholder="CVV"
                            className="w-1/2 p-2 border rounded"
                        />
                    </div>
                </div>
            </div> */}

            <div className="flex justify-center">
                <button
                    disabled={loading || (totalMembers > quantity) || (planName  == selectedPlan?.item?.name && planqty == quantity) }
                    className={`btn btn-blue
                        ${(loading || (totalMembers > quantity)) ? 'opacity-50 cursor-not-allowed' : ''}`}
                    onClick={handleRazorpayPayment}
                >
                    {loading ? 'Processing...' : isUpdate ? 'Update Subscription' : 'Subscribe Now'}
                </button>
            </div>
        </form>
    );
};

export default RazorpaySubscriptionForm;

