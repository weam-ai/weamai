'use client';
import React, { useState, useEffect } from 'react';
import useModal from '@/hooks/common/useModal';
import UpdateSubscription from '@/components/Subscription/UpdateSubscription';
import { timestampToDate, showPrice, showCurrencySymbol } from '@/utils/common';
import CancelSubscriptionModal from '../Settings/CancelSubscriptionModal';
import UpdateCardModal from '../Subscription/UpdateCardModal';
import { SUBSCRIPTION_STATUS } from '@/utils/constant';
import AlertDialogConfirmation from '../AlertDialogConfirmation';

const CurrentPlan = ({ subscriptionData, cancelSubscription, showDefaultPaymentMethod,
    paymentMethodData, unCancelSubscription, dataLoading }) => {
    const { isOpen, openModal, closeModal } = useModal();
    const { isOpen: isUnCancelOpen, openModal: openUnCancelModal, closeModal: closeUnCancelModal } = useModal();
    const [showCancelModal, setShowCancelModal] = useState(false);
    const [showUpdateCardModal, setShowUpdateCardModal] = useState(false);

    const handleCancelSubscription = (reason) => {
        const payload = { cancel_reason: reason }
        cancelSubscription(payload);
    };

    useEffect(() => {
        showDefaultPaymentMethod();
    }, [showUpdateCardModal]);

    const subscriptionItem = subscriptionData.items.data[0];
    const plan = subscriptionItem?.plan;
    const planName = subscriptionItem?.price?.product?.name;
    const planPriceId = subscriptionItem?.plan?.id;

    // Extract relevant details
    const basePricePerSet = showPrice(plan?.amount); // Price in dollars
    const membersPerSet = plan?.transform_usage?.divide_by || 1; // Number of members per set (e.g., 5)
    const qty = subscriptionItem?.quantity || 5; // Total quantity you have

    // Calculate the number of sets and total price
    const numOfSets = Math.ceil(qty / membersPerSet);
    const totalPrice = (numOfSets * (basePricePerSet as any)).toFixed(2); // Round to 2 decimal places

    const currency = plan?.currency;
    const interval = plan?.interval;
    const intervalCount = plan?.interval_count;
    const startDate = timestampToDate(subscriptionData.current_period_start);
    const endDate = timestampToDate(subscriptionData.current_period_end);

    const status = subscriptionData.subscriptionStatus;   //Status from our database
    const cancelDate = subscriptionData.cancel_at
        ? timestampToDate(subscriptionData.cancel_at)
        : null;

    return (
        <>
            <div className="plan-detail [.plan-detail+&]:mt-11">
                <div className="flex justify-between mt-5 mb-5 flex-col md:flex-row">
                    <div className="flex-1 md:pr-5 text-center md:text-left">
                        <p className="text-b6 text-font-14 mb-1">
                            {planName} ({qty} Users)
                        </p>
                        <h2 className="text-font-24 font-bold text-b2">
                            {showCurrencySymbol(currency)}{totalPrice} / {interval}(s)
                        </h2>
                        <p className="text-b6 text-font-14 mt-1.5">
                            {status == SUBSCRIPTION_STATUS.PENDING_CANCELLATION ? (
                                <p className="text-b6 text-font-14 bg-b12 px-3 py-1 rounded-md inline-block">
                                    Valid till {cancelDate}
                                </p>
                            ) : ''
                            }
                            {status == SUBSCRIPTION_STATUS.ACTIVE ? (
                                <>
                                    <p>
                                        Your plan renews on <div className='font-bold text-b2 text-font-18'>{timestampToDate(subscriptionData.current_period_end)}</div>
                                    </p>
                                </>
                            ) : ''
                            }
                        </p>

                    </div>
                    <div className="flex flex-col gap-2.5 md:ml-auto md:mt-0 mt-3 items-center md:items-end">
                        <div className='flex items-center md:justify-end'>
                            <p className="text-b6 text-font-14">
                                Status
                            </p>
                            <p className={`text-font-14 ml-2 px-3 py-1 rounded-full text-white ${status == SUBSCRIPTION_STATUS.PENDING_CANCELLATION ? 'bg-orange' : (status === SUBSCRIPTION_STATUS.ACTIVE ? 'bg-green' : 'bg-red')}`}>
                                {status.replace(/_/g, " ")}
                            </p>
                        </div>
                        {status == SUBSCRIPTION_STATUS.PENDING_CANCELLATION ? (
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
                                <div className='flex gap-3'>
                                    {status == SUBSCRIPTION_STATUS.ACTIVE && (
                                        <button
                                            type="button"
                                            className="btn btn-outline-gray w-[140px]"
                                            onClick={() => setShowCancelModal(true)}
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
                        <UpdateCardModal
                            open={showUpdateCardModal}
                            closeModal={() => {
                                setShowUpdateCardModal(false);
                                showDefaultPaymentMethod();
                            }}
                        />
                        <UpdateSubscription
                            open={isOpen}
                            closeModal={closeModal}
                            planqty={qty}
                            planPriceId={planPriceId}
                        />
                    </div>
                </div>
                <hr />
                <div className='mt-5 flex gap-4 justify-between flex-col md:flex-row'>
                    <div className="rounded-10 bg-b12 w-full px-5 py-3">
                        <ul role="list" className="*:py-1.5">
                            <li className="flex items-center justify-between relative">
                                <p className="text-b6 text-font-14">
                                    Plan Price
                                </p>
                                <p className="text-b6 text-font-14">
                                    {showCurrencySymbol(currency)}{basePricePerSet} / {interval} ({membersPerSet} users)
                                </p>
                            </li>
                            <li className="flex items-center justify-between relative">
                                <p className="text-b6 text-font-14">
                                    Users
                                </p>
                                <p className="text-b6 text-font-14">
                                    {qty}
                                </p>
                            </li>
                            <li className="flex items-center justify-between relative">
                                <hr className='w-full' />
                            </li>
                            <li className="flex items-center justify-between relative">
                                <p className="text-b3 text-font-14 font-bold">
                                    Total Price
                                </p>
                                <p className="text-b3 text-font-14 font-bold">
                                    {showCurrencySymbol(currency)}{totalPrice} / {interval}(s)
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
                                <p className="text-b6 text-font-14">
                                    End Date
                                </p>
                                <p className="text-b6 text-font-14">
                                    {endDate}
                                </p>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className='flex justify-between items-center p-4 bg-b12 my-3 rounded-md'>
                    <div>
                        <p className={`text-b6 text-font-14 ${!paymentMethodData?.last4 ? "text-red" : ""}`}>
                            {paymentMethodData?.last4 ?
                                `**** **** ${paymentMethodData.last4} (${paymentMethodData.brand})` :
                                "No Default Card Added"}
                        </p>
                    </div>
                    <div>
                        <button
                            type="button"
                            className="btn btn-blue w-[160px]"
                            onClick={() => setShowUpdateCardModal(true)}
                        >
                            Update Card
                        </button>
                    </div>
                </div>
            </div>
            {isUnCancelOpen && (
                <AlertDialogConfirmation
                    description={'Are you sure you want to activate subscription?'}
                    btntext={dataLoading ? 'Processing...' : 'Activate'}
                    btnclassName={'btn-blue'}
                    open={openUnCancelModal}
                    closeModal={closeUnCancelModal}
                    handleDelete={unCancelSubscription}
                    loading={dataLoading}
                />
            )}
        </>
    );

};

export default CurrentPlan;