import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import Label from '@/widgets/Label';
import  Toast  from '@/utils/toast';

const CancelSubscriptionModal = ({ open, closeModal, onConfirmCancel }) => {
    const [cancelReason, setCancelReason] = useState('');

    const handleSubmit = () => {
        if (cancelReason.trim().length < 10 || cancelReason.trim().length > 500) {
            Toast('Reason must be 10 to 500 characters long', 'error');
            return;
        }
        onConfirmCancel(cancelReason);
        closeModal();
        setCancelReason('');
    };

    return (
        <Dialog open={open} onOpenChange={closeModal}>
            <DialogContent className="md:max-w-[600px] max-w-[calc(100%-30px)] py-7">
                <DialogHeader className="rounded-t-10 px-[30px] pb-5 border-b">
                    <DialogTitle className="font-semibold flex items-center">
                        Cancel Subscription
                    </DialogTitle>
                </DialogHeader>
                <div className="dialog-body p-[30px]">
                    <Label title={"Please let us know why you`re canceling your subscription:"} />
                    <textarea
                        value={cancelReason}
                        onChange={(e) => setCancelReason(e.target.value)}
                        placeholder="Enter your reason for cancellation..."
                        maxLength={50}
                        className="min-h-[120px] mb-6 w-full p-2 border rounded-md"
                        minLength={10}
                        required
                    />
                    <div className="flex justify-end gap-3">
                        <Button variant="outline" onClick={closeModal}>
                            Cancel
                        </Button>
                        <Button onClick={handleSubmit}
                            className="btn btn-blue">
                            Confirm Cancellation
                        </Button>
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
};

export default CancelSubscriptionModal; 