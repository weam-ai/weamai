
import React from "react";

import { AlertDialogTitle, AlertDialog, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTrigger } from "./ui/alert-dialog";

const AlertDialogConfirmation = ({open, closeModal, description, btntext, btnclassName, handleDelete, loading, id}:any) => {
    return (
        <AlertDialog open={open} onOpenChange={closeModal}>
            <AlertDialogContent className="max-w-[450px] p-[30px]">
                <AlertDialogTitle></AlertDialogTitle>
                <AlertDialogHeader>
                <AlertDialogDescription className='text-font-16 font-semibold text-b2 mb-[18px] text-center break-all'>
                    {description}
                </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter className="justify-center space-x-2.5">
                <AlertDialogCancel className='btn btn-outline-gray'>Cancel</AlertDialogCancel>
                    <button className={`btn ${btnclassName} ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}  
                        onClick={() => handleDelete(id)} disabled={loading}>{btntext}
                    </button>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
};

export default AlertDialogConfirmation;