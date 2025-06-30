'use client';

import useModal from '@/hooks/common/useModal';
import RequestMoreStorageModal from '../RequestMoreStorageModal';

const StorageAction = () => {
    const { isOpen, openModal, closeModal } = useModal();
    return (
        <>
            <button className="btn btn-outline-gray" onClick={openModal}>
                Request For More Storage
            </button>
            {isOpen && (
                <RequestMoreStorageModal
                    open={isOpen}
                    closeModal={closeModal}
                />
            )}
        </>
    );
};

export default StorageAction;
