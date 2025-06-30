'use client';
import React from 'react';
import useModal from '@/hooks/common/useModal';
import PlusButton from '@/components/PlusButton';
import UpdateInformationModal from '@/components/Settings/UpdateInformationModal';

const BillingInfo = () => {
    const data = [
        { id: 1, field: 'Name', value: 'William Watson' },
        {
            id: 2,
            field: 'Billing address',
            value: '903 Main Street Hanson, MA 02341 US',
        },
        { id: 3, field: 'Contact No', value: '+44 866 283 2227' },
        { id: 4, field: 'Email', value: 'example@agencyname.com' },
    ];
    const { isOpen, openModal, closeModal } = useModal();
    
    return (
        <div className="plan-detail [.plan-detail+&]:mt-11">
            <h5 className="text-font-16 font-semibold text-b2 mb-5 border-b border-b11 pb-1.5">
                Billing Information
            </h5>
            <table>
                <tbody>
                    {data.map((billinfo) => (
                        <tr className="pt-10" key={billinfo.id}>
                            <td className="text-font-14 text-b6 py-1 px-4 first:pl-0 last:pr-0">
                                {billinfo.field}:{' '}
                            </td>
                            <td className="text-font-14 text-b2 py-1 px-4 first:pl-0 last:pr-0">
                                {billinfo.value}{' '}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <PlusButton
                text={'Update information'}
                className="mt-5"
                onClick={() => openModal()}
            />
            {isOpen && (
                <UpdateInformationModal
                    open={openModal}
                    closeModal={closeModal}
                />
            )}
        </div>
    );
};

export default BillingInfo;