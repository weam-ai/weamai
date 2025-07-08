
import React, { useState } from 'react';
import Datatable from '@/components/DataTable/DataTable';
import DataTableSearch from '@/components/DataTable/DataTableSearch';
import DataTablePageSizeSelector from '@/components/DataTable/DataTablePageSizeSelector';
import DataTablePagination from '@/components/DataTable/DataTablePagination';
import CommonInput from '@/widgets/CommonInput';

export default function CreditTransaction() {

     
    return (
        <div className='max-w-[100vw]'>
            <div className="mb-4">
                <h2 className="font-bold">Credit Transaction Audit Log</h2>
                <p className='text-font-14 mb-3'>Complete history of all credit-related activities in your organization</p>
                <CommonInput className="default-form-input" type="text" placeholder="Search" />
                <div className="border p-4 bg-white rounded-md w-full mt-3 mb-3 flex items-center gap-x-2 max-md:flex-wrap">
                    <div className='w-[170px]'>
                        <div className="font-medium">John Admin</div>
                        <div className="text-font-12 text-b7">john@acme.com</div>
                    </div>
                    <div className="text-font-12 text-b7">Purchased 500 credits for $40</div>
                    <div className='ml-auto flex items-center gap-x-2 max-md:w-full max-md:mt-2'>
                        <div className='rounded-large border px-2 py-1 text-font-12 inline-block'>Purchase</div>
                        <div className='text-font-12 text-b6'>Jan 15, 2024, 04:00PM</div>
                    </div>
                </div>
                <div className="border p-4 bg-white rounded-md w-full mt-3 mb-3 flex items-center gap-x-2 max-md:flex-wrap">
                    <div className='w-[170px]'>
                        <div className="font-medium">Smith Joi</div>
                        <div className="text-font-12 text-b7">smith@acme.com</div>
                    </div>
                    <div className="text-font-12 text-b7">Smith Joi Allocated 100 credits to Alice Johnson</div>
                    <div className='ml-auto flex items-center gap-x-2 max-md:w-full max-md:mt-2'>
                        <div className='rounded-large border px-2 py-1 text-font-12 inline-block'>Allocate</div>
                        <div className='text-font-12 text-b6'>Jan 15, 2024, 04:00PM</div>
                    </div>
                </div>
                
            </div>
        </div>
    );
}