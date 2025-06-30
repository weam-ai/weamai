import React from 'react';
import DeleteDialog from '../Shared/DeleteDialog';

const DeleteAccount = () => {
    return (
        <div className="setting-collapse-item flex justify-between items-center rounded-10 border border-b11 bg-b12 py-[11px] px-5 [.setting-collapse-item+&]:mt-2.5">
            <h3 className="text-font-16 font-semibold text-b2 ">
                Delete Account
            </h3>
            <DeleteDialog
                title={'Are you sure you want to delete account?'}
                visible={true}
            />
        </div>
    );
};

export default DeleteAccount;
