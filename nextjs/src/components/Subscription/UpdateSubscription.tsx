"use client";
import React from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from "@/components/ui/dialog"
import UpgradeIcon from '@/icons/UpgradeIcon';
import SubscriptionForm from './SubscriptionForm';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { STRIPE_PUBLISH_KEY } from '@/config/config';
import { getCurrentUser } from '@/utils/handleAuth';
import RazorpaySubscriptionForm from './RazorPaySubscriptionForm';
const stripePromise = loadStripe(STRIPE_PUBLISH_KEY);

const UpdateSubscription = ({ open, closeModal, planqty, planPriceId, planName }:any) => {
   
   const user = getCurrentUser();
   return (
      <Dialog open={open} onOpenChange={() => closeModal()}>
         <DialogContent className="md:max-w-[730px] max-w-[calc(100%-30px)] py-7">
            <DialogHeader className="rounded-t-10 px-[30px] pb-5 border-b">
               <DialogTitle className="font-semibold flex items-center">
                  <UpgradeIcon width={'24'} height={'24'} className={'me-3 inline-block align-middle fill-b1'} />
                  Update Your Plan
               </DialogTitle>
            </DialogHeader>
            <div className="dialog-body h-full p-[30px] overflow-x-hidden max-h-[650px] overflow-y-auto">
               {user?.countryCode == 'IN' && user?.company?.name?.startsWith("Razorpay") ? (
                  <RazorpaySubscriptionForm
                     isUpdate={true}
                     closeModal={closeModal}
                     planqty={planqty}
                     planName={planName}
                  />
               ) : (
                  <Elements stripe={stripePromise}>
                     <SubscriptionForm
                        isUpdate={true}
                        closeModal={closeModal}
                        planqty={planqty}
                        planPriceId={planPriceId}
                     />
                  </Elements>
               )
               }
            </div>
         </DialogContent>
      </Dialog>

   );
};

export default UpdateSubscription;
