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

type MCPDisconnectDialogProps = {
    open: boolean;
    closeModal: () => void;
    onDisconnect: () => void;
    serviceName: string;
    serviceIcon?: React.ReactNode;
    description?: string;
    btnText?: string;
    btnClass?: string;
    loading?: boolean;
    buttonVisible?: boolean;
}

const MCPDisconnectDialog: React.FC<MCPDisconnectDialogProps> = ({
    open,
    closeModal,
    onDisconnect,
    serviceName,
    serviceIcon,
    description,
    btnText,
    btnClass = "btn-red",
    loading = false,
}) => {
    const defaultDescription = `Are you sure you want to disconnect your ${serviceName} account? This will remove all ${serviceName} integrations and stop all automation.`;
    const defaultBtnText = `Disconnect ${serviceName}`;

    return (
        <AlertDialog open={open} onOpenChange={closeModal}>
            <AlertDialogContent className="max-w-[450px] p-[30px]">
                <AlertDialogHeader>
                    {serviceIcon && (
                        <div className="flex items-center justify-center mb-4">
                            {serviceIcon}
                        </div>
                    )}
                    <AlertDialogDescription className="text-font-16 font-semibold text-b2 mb-[18px] text-center">
                        <AlertDialogTitle>
                            Disconnect {serviceName}
                        </AlertDialogTitle>
                        <p className="text-font-14 text-b6 mt-2 text-center mb-4 font-normal">
                            {description || defaultDescription}
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
                        {loading ? 'Disconnecting...' : (btnText || defaultBtnText)}
                    </button>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
};

export default MCPDisconnectDialog; 