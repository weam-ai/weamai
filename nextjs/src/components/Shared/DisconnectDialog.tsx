import React from 'react';
import {
    AlertDialog,
    AlertDialogTitle,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

type DisconnectDialogProps = {
    open: boolean;
    closeModal: () => void;
    onDisconnect: () => void;
    title?: string;
    description?: string;
    btnText?: string;
    btnClass?: string;
    loading?: boolean;
    buttonVisible?: boolean;
}

const DisconnectDialog = ({
    open,
    closeModal,
    onDisconnect,
    title = "Disconnect Integration",
    description = "Are you sure you want to disconnect this integration? This will remove all connections and stop all automation.",
    btnText = "Disconnect",
    btnClass = "btn-red",
    loading = false,
    buttonVisible = false
}: DisconnectDialogProps) => {
    return (
        <AlertDialog open={open} onOpenChange={closeModal}>
            {buttonVisible && (
                <AlertDialogTrigger className={`btn ${btnClass}`}>
                    {btnText}
                </AlertDialogTrigger>
            )}
            <AlertDialogContent className="max-w-[450px] p-[30px]">
                <AlertDialogHeader>
                    <AlertDialogDescription className="text-font-16 font-semibold text-b2 mb-[18px] text-center">
                        <AlertDialogTitle>
                            {title}
                        </AlertDialogTitle>
                        <p className="text-font-14 text-b6 mt-2 text-center">
                            {description}
                        </p>
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter className="justify-center space-x-2.5">
                    <AlertDialogCancel className="btn btn-outline-gray" onClick={closeModal}>
                        Cancel
                    </AlertDialogCancel>
                    <button 
                        className={`btn ${btnClass} ${loading ? 'opacity-50 cursor-not-allowed' : ''}`} 
                        onClick={onDisconnect} 
                        disabled={loading}
                    >
                        {loading ? 'Disconnecting...' : btnText}
                    </button>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
};

export default DisconnectDialog; 