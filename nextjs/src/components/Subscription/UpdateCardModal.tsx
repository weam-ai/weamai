import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useStripe, CardElement, Elements, useElements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import { useSubscription } from '@/hooks/subscription/useSubscription';
import { STRIPE_PUBLISH_KEY } from '@/config/config';
import Label from '@/widgets/Label';
// Initialize Stripe outside of component (typically with your publishable key)
const stripePromise = loadStripe(STRIPE_PUBLISH_KEY);

const UpdateCardModal = ({ open, closeModal }) => {
    const [error, setError] = useState(null);
    const stripe = useStripe();
    const elements = useElements();
    const { updatePaymentMethod, loading } = useSubscription();

    const handleSubmit = async () => {
        if (!stripe || !elements) {
            return;
        }

        setError(null);

        try {
            const { error: stripeError, paymentMethod } = await stripe.createPaymentMethod({
                type: 'card',
                card: elements.getElement(CardElement),
            });

            if (stripeError) {
                setError(stripeError.message);
                return;
            }
            const payload = {
                paymentMethodId: paymentMethod.id,
            };
            await updatePaymentMethod(payload);
            closeModal();
        } catch (err) {
            setError(err.message || 'An error occurred while updating your card.');
        }
    };

    return (
        <Dialog open={open} onOpenChange={closeModal}>
            <DialogContent className="md:max-w-[600px] max-w-[calc(100%-30px)] py-7">
                <DialogHeader className="rounded-t-10 px-[30px] pb-5 border-b">
                    <DialogTitle className="font-semibold flex items-center">
                        Update Card Details
                    </DialogTitle>
                </DialogHeader>
                <div className="dialog-body p-[30px]">
                    <Label title={"Enter new card details"} />
                    
                    <div className="mb-6">
                        <CardElement 
                            options={{
                                style: {
                                    base: {
                                        fontSize: '14px',
                                        color: '#424770',
                                        '::placeholder': {
                                            color: '#aab7c4',
                                        },
                                    },
                                    invalid: {
                                        color: '#9e2146',
                                    },
                                }
                            }}
                        />
                        {error && (
                            <div className="text-font-13 font-medium mt-1 text-red">{error}</div>
                        )}
                    </div>
                    <div className="flex justify-end gap-3">
                        <Button 
                            variant="outline" 
                            onClick={closeModal} 
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button 
                            onClick={handleSubmit}
                            className="btn btn-blue w-[160px]"
                            disabled={loading || !stripe}
                        >
                            {loading ? 'Processing...' : 'Update Card'}
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

// Wrap the existing modal component
const UpdateCardModalWrapper = (props) => (
  <Elements stripe={stripePromise}>
    <UpdateCardModal {...props} />
  </Elements>
);

export default UpdateCardModalWrapper; 