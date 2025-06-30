'use client';
import React, { useState, useEffect } from 'react';
import useModal from '@/hooks/common/useModal';
import UpdateSubscription from '@/components/Subscription/UpdateSubscription';
import { timestampToDate, showPrice, showCurrencySymbol } from '@/utils/common';
import CancelSubscriptionModal from '../Settings/CancelSubscriptionModal';
import { RAZORPAY_SUBSCRIPTION_STATUS } from '@/utils/constant';
import AlertDialogConfirmation from '../AlertDialogConfirmation';
import { RAZORPAY } from '@/config/config';
import Toast from '@/utils/toast';
import { getCurrentUser } from '@/utils/handleAuth';
import { useRazorpaySubscription } from '@/hooks/subscription/useRazorpaySubscription';
import RazorpaySubscriptionOptions from '@/types/subscription';

const RazorpayCurrentPlan = ({
    subscriptionData,
    cancelSubscription,
    showDefaultPaymentMethod,
    paymentMethodData,
    unCancelSubscription,
    dataLoading,
    onRefresh,
}: any) => {

    const { isOpen, openModal, closeModal } = useModal();
    const {
        isOpen: isUnCancelOpen,
        openModal: openUnCancelModal,
        closeModal: closeUnCancelModal,
    } = useModal();
    const { updateRazorpayCard } = useRazorpaySubscription();
    const [showCancelModal, setShowCancelModal] = useState(false);

    const currentUser = getCurrentUser();
    const handleCancelSubscription = (reason) => {
        const payload = { cancel_reason: reason };
        cancelSubscription(payload);
    };

    useEffect(() => {
        showDefaultPaymentMethod();
    }, []);

    const handleUnCancel = async () => {
        try {
            await unCancelSubscription();
            onRefresh(); // Call the callback to refresh subscription data
            closeUnCancelModal();
        } catch (error) {
            console.error('Error uncancelling subscription:', error);
            Toast('An error occurred while activating the subscription.');
        }
    };


    //
    const subscriptionItem = subscriptionData;
    const plan = subscriptionItem?.plan;
    const planName = subscriptionItem?.planName;
    const planPriceId = subscriptionItem?.plan?.id;

    // Extract relevant details
    const basePricePerSet: any = showPrice(subscriptionItem?.planAmount);
    const membersPerSet = plan?.transform_usage?.divide_by || 1; // Number of members per set (e.g., 5)
    const qty = subscriptionItem?.quantity || 5; // Total quantity you have

    const totalPrice = (qty * basePricePerSet).toFixed(2); // Round to 2 decimal places

    const currency = subscriptionItem?.planCurrency;
    const interval = plan?.interval;
    const startDate = timestampToDate(subscriptionData.current_start);
    const endDate = timestampToDate(subscriptionData.current_end);

    const status = subscriptionData.subscriptionStatus; //Status from our database
    const cancelDate = subscriptionData.current_end
        ? timestampToDate(subscriptionData.current_end)
        : null;

    const handleUpdateCard = async () => {
        try {
            const options: RazorpaySubscriptionOptions = {
                key: RAZORPAY.KEY_ID,
                // subscription_id: `${subscriptionData.id}`,
                customer_id: "cust_QREmXpzoTpJMvZ",
                name: 'Weam',
                description: 'Update payment method',
                method: {
                    netbanking: false,
                    card: true,
                    upi: false,
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
                },
                saved_cards: 1, // Show saved cards
                subscription_card_change: 1, // Enables updating payment method
                recurring: 1,
                handler: function (response) {
                    if(response?.razorpay_payment_id){
                        updateRazorpayCard({
                            payment_id: response?.razorpay_payment_id,
                            subscription_id: subscriptionData?.id,
                            payment_method: 'card'
                        });
                    }
                    
                    showDefaultPaymentMethod();
                
                },
                prefill: {
                    name: currentUser?.fname + ' ' + currentUser?.lname,
                    email: currentUser?.email,
                },
                theme: { color: '#6737ec' },
            };

            const rzp1 = new (window as any).Razorpay(
                options as RazorpaySubscriptionOptions
            );
            rzp1.open();
        } catch (error) {
            console.error('Error updating card:', error);
            Toast('An error occurred while updating the card.');
        }
    };

    const handleUpdateUPI = () => {
        //write a code for update upi 
        const options: RazorpaySubscriptionOptions = {
            key: RAZORPAY.KEY_ID,
            subscription_id: `${subscriptionData.id}`,
            name: 'Weam',
            description: 'Update payment method',
            handler: function (response) {
                console.log('UPI Added Successfully:', response);
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

        const rzp1 = new (window as any).Razorpay(
            options as RazorpaySubscriptionOptions
        );
        rzp1.open();
    };

    useEffect(() => {
        // Dynamically load Razorpay script
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        document.body.appendChild(script);
        return () => {
            document.body.removeChild(script);
        };
    }, []);

    return (
        <>
            <div className="plan-detail [.plan-detail+&]:mt-11">
                <div className="flex justify-between mt-5 mb-5 flex-col md:flex-row">
                    <div className="flex-1 md:pr-5 text-center md:text-left">
                        <p className="text-b6 text-font-14 mb-1">
                            {planName} ({qty} Users)
                        </p>
                        <h2 className="text-font-24 font-bold text-b2">
                            {showCurrencySymbol(currency)}
                            {totalPrice}
                        </h2>
                        <p className="text-b6 text-font-14 mt-1.5">
                            {status ==
                            RAZORPAY_SUBSCRIPTION_STATUS.PENDING_CANCELLATION ? (
                                <p className="text-b6 text-font-14 bg-b12 px-3 py-1 rounded-md inline-block">
                                    Valid till {cancelDate}
                                </p>
                            ) : (
                                ''
                            )}
                            {status == RAZORPAY_SUBSCRIPTION_STATUS.ACTIVE ? (
                                <>
                                    <p>
                                        Your plan renews on{' '}
                                        <div className="font-bold text-b2 text-font-18">
                                            {timestampToDate(
                                                subscriptionData.current_end
                                            )}
                                        </div>
                                    </p>
                                </>
                            ) : (
                                ''
                            )}
                        </p>
                    </div>
                    <div className="flex flex-col gap-2.5 md:ml-auto md:mt-0 mt-3 items-center md:items-end">
                        <div className="flex items-center md:justify-end">
                            <p className="text-b6 text-font-14">Status</p>
                            <p
                                className={`text-font-14 ml-2 px-3 py-1 rounded-full text-white ${
                                    status ==
                                    RAZORPAY_SUBSCRIPTION_STATUS.PENDING_CANCELLATION
                                        ? 'bg-orange'
                                        : status ===
                                          RAZORPAY_SUBSCRIPTION_STATUS.ACTIVE
                                        ? 'bg-green'
                                        : 'bg-red'
                                }`}
                            >
                                {status.replace(/_/g, ' ')}
                            </p>
                        </div>
                        {status ==
                        RAZORPAY_SUBSCRIPTION_STATUS.PENDING_CANCELLATION ? (
                            <>
                                <button
                                    type="button"
                                    className={`btn btn-red w-[160px] ${dataLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                                    onClick={() => openUnCancelModal()}
                                    disabled={dataLoading}
                                >
                                    {dataLoading ? 'Processing...' : "Don't Cancel"}
                                </button>
                            </>
                        ) : (
                            <>
                                <div className="flex gap-3">
                                    {status ==
                                        RAZORPAY_SUBSCRIPTION_STATUS.ACTIVE && (
                                        <button
                                            type="button"
                                            className="btn btn-outline-gray w-[140px]"
                                            onClick={() =>
                                                setShowCancelModal(true)
                                            }
                                        >
                                            Cancel Plan
                                        </button>
                                    )}
                                    <button
                                        type="button"
                                        className="btn btn-blue w-[140px]"
                                        onClick={() => openModal()}
                                    >
                                        Update Plan
                                    </button>
                                </div>
                            </>
                        )}

                        <CancelSubscriptionModal
                            open={showCancelModal}
                            closeModal={() => setShowCancelModal(false)}
                            onConfirmCancel={handleCancelSubscription}
                        />
                        <UpdateSubscription
                            open={isOpen}
                            closeModal={closeModal}
                            planqty={qty}
                            planName={planName}
                            planPriceId={planPriceId}
                        />
                    </div>
                </div>
                <hr />
                <div className="mt-5 flex gap-4 justify-between flex-col md:flex-row">
                    <div className="rounded-10 bg-b12 w-full px-5 py-3">
                        <ul role="list" className="*:py-1.5">
                            <li className="flex items-center justify-between relative">
                                <p className="text-b6 text-font-14">
                                    Plan Price
                                </p>
                                <p className="text-b6 text-font-14">
                                    {showCurrencySymbol(currency)}
                                    {basePricePerSet} / {interval} (
                                    {membersPerSet} users)
                                </p>
                            </li>
                            <li className="flex items-center justify-between relative">
                                <p className="text-b6 text-font-14">Users</p>
                                <p className="text-b6 text-font-14">{qty}</p>
                            </li>
                            <li className="flex items-center justify-between relative">
                                <hr className="w-full" />
                            </li>
                            <li className="flex items-center justify-between relative">
                                <p className="text-b3 text-font-14 font-bold">
                                    Total Price
                                </p>
                                <p className="text-b3 text-font-14 font-bold">
                                    {showCurrencySymbol(currency)}
                                    {totalPrice}
                                </p>
                            </li>
                        </ul>
                    </div>
                    <div className="rounded-10 bg-b12 w-full px-5 py-3">
                        <ul role="list" className="*:py-1.5">
                            <li className="flex items-center justify-between relative">
                                <p className="text-b6 text-font-14">
                                    Start Date
                                </p>
                                <p className="text-b6 text-font-14">
                                    {startDate}
                                </p>
                            </li>
                            <li className="flex items-center justify-between relative">
                                <p className="text-b6 text-font-14">End Date</p>
                                <p className="text-b6 text-font-14">
                                    {endDate}
                                </p>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="flex justify-between items-center p-4 bg-b12 my-3 rounded-md">
                    <div>
                        {subscriptionData?.paymentMethod == 'card' ? (
                            <p
                                className={`text-b6 text-font-14 ${
                                    !paymentMethodData?.[0]?.last4
                                        ? 'text-red'
                                        : ''
                                }`}
                            >
                                {paymentMethodData?.[0]?.last4
                                    ? `**** **** ${paymentMethodData?.[0]?.last4} (${paymentMethodData?.[0]?.network})`
                                    : 'No Default Card Added'}
                            </p>
                        ) : (
                            <p
                                className={`text-b6 text-font-14 ${
                                    !subscriptionData.paymentDetails?.contact
                                        ? 'text-red'
                                        : ''
                                }`}
                            >
                                {subscriptionData.paymentDetails?.contact
                                    ? `${subscriptionData.paymentDetails.contact}`
                                    : 'No Default UPI Added'}
                            </p>
                        )}
                    </div>
                    <div>
                        {subscriptionData.paymentMethod == 'card' ? (
                            <button
                                type="button"
                                className="btn btn-blue w-[160px]"
                                onClick={handleUpdateCard}
                            >
                                Update Card
                            </button>
                        ) : (
                            <button
                                type="button"
                                className="btn btn-blue w-[160px]"
                                onClick={handleUpdateUPI}
                            >
                                Update UPI
                            </button>
                        )}
                    </div>
                </div>
            </div>
            {isUnCancelOpen && (
                <AlertDialogConfirmation
                    description={
                        'Are you sure you want to activate subscription?'
                    }
                    btntext={dataLoading ? 'Processing...' : 'Activate'}
                    btnclassName={'btn-blue'}
                    open={openUnCancelModal}
                    closeModal={closeUnCancelModal}
                    handleDelete={handleUnCancel}
                    loading={dataLoading}
                />
            )}
        </>
    );
};

export default RazorpayCurrentPlan;