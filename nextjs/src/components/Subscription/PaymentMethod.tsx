'use client';
import React, { useState } from 'react';
import Image from 'next/image';
import VisaIcon from '@/../public/visa-icon.svg';
import RemoveIcon from '@/icons/RemoveIcon';
import PlusButton from '@/components/PlusButton';
import AlertDialogConfirmation from '@/components/AlertDialogConfirmation';
import AddNewCardModal from '@/components/Settings/AddNewCardModal';
import useModal from '@/hooks/common/useModal';

const PaymentMethod = () => {
    const { isOpen, openModal, closeModal } = useModal();
    const {
        isOpen: addNewCard,
        openModal: addNewCardOpen,
        closeModal: closeNewCard,
    } = useModal();
    const [match, setMatch] = useState(1);
    const data = [{ id: 1 }, { id: 2 }, { id: 3 }, { id: 4 }];

    return (
        <div className="plan-detail [.plan-detail+&]:mt-11">
            <h5 className="text-font-16 font-semibold text-b2 mb-5 border-b border-b11 pb-1.5">
                Payment Method
            </h5>
            <table className="table">
                <thead>
                    <tr>
                        <th>Cart Type</th>
                        <th>Ending in</th>
                        <th>Expires</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody className="border-b border-11">
                    {data.map((p) => (
                        <tr key={p.id}>
                            <td className="text-nowrap">
                                <Image
                                    src={VisaIcon}
                                    alt="visa"
                                    height={14}
                                    width={44}
                                    className="w-11 h-[14px] min-w-11 object-contain me-5 inline-block"
                                />{' '}
                                Visa
                            </td>
                            <td className="text-nowrap">XXXX XXXX XXXX 1111</td>
                            <td>05/30</td>
                            <td className="text-right">
                                <button onClick={() => openModal()}>
                                    <RemoveIcon
                                        className={'w-4 h-4 fill-b4 hover:fill-red object-contain'}
                                        width={16}
                                        height={16}
                                    />
                                </button>
                                {isOpen && p.id === match && (
                                    <AlertDialogConfirmation
                                        description={'Are you sure you want to delete?'}
                                        btntext={'Delete'}
                                        btnclassName={'btn-red'}
                                        open={openModal}
                                        closeModal={closeModal}
                                    />
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <PlusButton
                text={'Add Card'}
                className="mt-5"
                onClick={() => addNewCardOpen()}
            />
            {addNewCard && (
                <AddNewCardModal
                    open={addNewCardOpen}
                    closeModal={closeNewCard}
                />
            )}
        </div>
    );
};

export default PaymentMethod;