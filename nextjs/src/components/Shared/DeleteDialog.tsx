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

const DeleteDialog = ({ title, openModel, closeModel, onDelete,buttonVisible=true, btnText="Delete", btnClass="btn-red" }:any) => {
  
    
    return (
        <AlertDialog open={openModel} close={closeModel}>

           {buttonVisible && <AlertDialogTrigger className={`btn ${btnClass}`}>
                {btnText}
            </AlertDialogTrigger>}
            <AlertDialogContent className="max-w-[450px] p-[30px]">
                <AlertDialogHeader>
                    <AlertDialogDescription className="text-font-16 font-semibold text-b2 mb-[18px] text-center">
                        <AlertDialogTitle>
                            {title}
                        </AlertDialogTitle>
                    </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter className="justify-center space-x-2.5">
                    <AlertDialogCancel className="btn btn-outline-gray" onClick={closeModel}>
                        Cancel
                    </AlertDialogCancel>
                    <button className={`btn ${btnClass}`} onClick={onDelete}>{btnText}</button>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
};

export default DeleteDialog;
