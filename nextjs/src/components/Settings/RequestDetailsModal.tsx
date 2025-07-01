import React, { useState, useEffect, useMemo } from 'react';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogClose } from "@/components/ui/dialog"
import { setRequestDetailsModalAction } from '@/lib/slices/modalSlice';
import { useDispatch } from 'react-redux';
import { bytesToMegabytes, megabytesToBytes, showCurrencySymbol, showPrice } from '@/utils/common';
import StorageSelector from '../StorageSelector';
import useStorage from '@/hooks/storage/useStorage';
import { getCurrentUser } from '@/utils/handleAuth';
import { STRIPE_PUBLISH_KEY } from '@/config/config';
import Toast from '@/utils/toast';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';

const stripePromise = loadStripe(STRIPE_PUBLISH_KEY);

const Wrapper = ({ children }) => {
    return (
        <Elements stripe={stripePromise}>
            {children}
        </Elements>
    );
};

const RequestDetailsModal = ({ closeModal, selectedRequest, setRefreshStorageRequests, refreshStorageRequests }:any) => {
    const dispatch = useDispatch();
    const user = useMemo(()=>getCurrentUser(),[])

    const [defaultStorageValue, setDefaultStorageValue] = useState<any>(bytesToMegabytes(selectedRequest?.requestSize));

    const {
        approveStorageRequest,
        declineStorageRequest,
        loading,
        dataLoading,        
    } = useStorage();

    const handleOpen = () => {
        dispatch(setRequestDetailsModalAction(true));
    };

    const handleDecline = async () => {
        const payload = {
            storageRequestId: selectedRequest?._id
        }
        await declineStorageRequest(payload);
        setRefreshStorageRequests(true);
        closeModal();
    }

    const BodyContent = () => {
       
        const onApprove = async () => {
            try {    
                const payload = {
                    storageRequestId: selectedRequest?._id,
                    updatedStorageSize: megabytesToBytes(defaultStorageValue),
                    amount: 0,
                    currency: 'USD'
                }
                const response = await approveStorageRequest(payload);
            } catch (error) {
                console.error(error);
            }
        }

        return (
            <Dialog open={handleOpen} onOpenChange={closeModal}>
                <DialogContent className="md:max-w-[500px] max-w-[calc(100%-30px)]">
                    <DialogHeader>
                        <DialogTitle className="rounded-t-10 text-font-18 font-bold text-b2 bg-b12 px-[30px] py-6 border-b borer-b11">
                            Storage Request Details
                        </DialogTitle>
                    </DialogHeader>
                    <div className="dialog-body h-full">
                        <table className='w-full text-font-14 text-b5 text-left mb-5'>
                            <tbody>
                                <tr className='border-b border-b10 *:px-[30px] *:py-3'>
                                    <th className='text-b2 font-semibold'>Name</th>
                                    <td>{`${selectedRequest?.user?.fname} ${selectedRequest?.user?.lname}`}</td>
                                </tr>
                                <tr className='border-b border-b10 *:px-[30px] *:py-3'>
                                    <th className='text-b2 font-semibold'>Email</th>
                                    <td>{selectedRequest?.user?.email}</td>
                                </tr>
                                <tr className='border-b border-b10 *:px-[30px] *:py-3'>
                                    <th className='text-b2 font-semibold'>Requested for</th>
                                    <td>Increase Storage by <span className='text-b2 font-semibold'>{bytesToMegabytes(selectedRequest?.requestSize)} mb</span></td>
                                </tr>
                                <tr className='border-b border-b10 *:px-[30px] *:py-3'>
                                    <th className='text-b2 font-semibold'>Approved Storage</th>
                                    <td>
                                        <StorageSelector className="bg-white" min={20} max={500}
                                            step={20}
                                            initialValue={defaultStorageValue}
                                            unit="mb"
                                            onChange={(newValue) => setDefaultStorageValue(newValue)} />
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                    <DialogFooter className="flex items-center justify-end gap-2.5 pb-[30px] px-[30px]">
                        <button className='btn btn-outline-gray'
                            onClick={handleDecline}
                            disabled={loading}>Decline</button>
                        <button className='btn btn-blue'
                            onClick={onApprove}
                            disabled={loading || dataLoading}>Approve</button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        );
    };


    // const getAmountDisplay = () => {
    //     if (subscriptionLoading || dataLoading) return 'Loading...';
    //     if (subscriptionData && user.countryCode==="IN" && user?.company?.name?.startsWith("Razorpay") && !dataLoading) {
    //         const amount = Number(showPrice(razorpayStoragePrice?.item?.unit_amount)) || 0;
    //         return `${showCurrencySymbol(subscriptionData?.planCurrency)} ${(amount * (defaultStorageValue/20)).toFixed(2)}`;
    //     }else if (subscriptionData && Object.keys(subscriptionData).length > 0 && !dataLoading) {
    //         const amount = Number(showPrice(productPrice?.unit_amount)) || 0;
    //         return `${showCurrencySymbol(subscriptionData?.currency)} ${(amount * defaultStorageValue/20).toFixed(2)}`;
    //     } 
    //     return NO_ACTIVE_SUBSCRIPTION_FOUND;
    // };

    // useEffect(() => {
    //     if(user.countryCode==='IN' && user?.company?.name?.startsWith("Razorpay")){
    //         getRazorpayStoragePrice()
    //     } else if (subscriptionData && Object.keys(subscriptionData).length > 0) {
    //         getStorageProductPrice(subscriptionData?.currency);
    //     }
    // }, [subscriptionData]);

    // useEffect(() => {
    //     user.countryCode==="IN" && user?.company?.name?.startsWith("Razorpay") ? fetchActiveSubscription(MODULE_ACTIONS.GET_RAZORPAY_SUBSCRIPTION) : fetchActiveSubscription(null);
    // }, []);

    // useEffect(() => {
    //     if(user.countryCode==="IN" && user?.company?.name?.startsWith("Razorpay")){
    //         const script = document.createElement('script');
    //         script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    //         script.async = true;
    //         document.body.appendChild(script);
    //         return () => {
    //             document.body.removeChild(script);
    //         };
    //     }
    // }, []);

    // Return the wrapped component
    return <Wrapper><BodyContent /></Wrapper>;
};

export default RequestDetailsModal;
