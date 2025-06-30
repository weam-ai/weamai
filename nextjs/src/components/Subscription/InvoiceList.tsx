import React, { useState, useEffect, useCallback } from 'react';
import Datatable from '@/components/DataTable/DataTable';
import DataTablePagination from '@/components/DataTable/DataTablePagination';
import DataTablePageSizeSelector from '@/components/DataTable/DataTablePageSizeSelector';
import DataTableSearch from '@/components/DataTable/DataTableSearch';
import {
    useReactTable,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
} from '@tanstack/react-table';
import { useSubscription } from '@/hooks/subscription/useSubscription';
import { dateDisplay, showCurrencySymbol } from '@/utils/common';

const InvoiceList = () => {
    const [columnFilters, setColumnFilters] = useState([]);
    const [sorting, setSorting] = useState([]);
    const [filterInput, setFilterInput] = useState('');
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const { getInvoiceList, invoiceList, loading, totalRecords } = useSubscription();

    useEffect(() => {
        const timer = setTimeout(()=>{
            getInvoiceList(filterInput, pagination.pageSize, (pagination.pageIndex) * pagination.pageSize);                    
        },500)

        return ()=> clearTimeout(timer)
    }, [pagination, filterInput, sorting, columnFilters]);

    const handleFilterChange = (e) => {
        const value = e.target.value || '';
        setColumnFilters((old) => [
            {
                id: 'email',
                value: value?.toLowerCase(),
            },
        ]);
        setFilterInput(value);
    };

    const handlePageSizeChange = (pageSize) => {
        setPagination((old) => ({ ...old, pageSize }));
    };

    useEffect(() => {
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    }, [filterInput]);

    const handleDownload = useCallback((invoiceUrl) => {
        if (invoiceUrl) {
            const link = document.createElement('a');
            link.href = invoiceUrl;
            link.download = ''; // You can specify a filename here if needed
            link.target = '_blank';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } else {
            console.error('Invoice URL is not available');
            alert('Invoice URL is not available');
        }
    }, []);

    let columns = [
        {
            header: 'Invoice No.',
            accessorKey: 'invoiceNo',
            cell: ({ row }) => '#' + (row?.original?.invoiceNo || row?.original?.invoiceId || 'N/A'),
        },
        {
            header: 'Date',
            accessorKey: 'createdAt',
            cell: ({ row }) => {
                const date = dateDisplay(row?.original?.createdAt); 
                return date ? date : 'N/A';
            },
        },
        {
            header: 'Description',
            accessorKey: 'description',
            cell: ({ row }) => { 
                const storage_request_id = row?.original?.storage_request_id || 'N/A';
                const is_subscription = row?.original?.is_subscription;
                return is_subscription ? `Subscription Renewal Charge` 
                    : `Charge for storage request (${storage_request_id})`;
            }
        },
        {
            header: 'Amount',
            accessorKey: 'total',
            cell: ({ row }) => `${showCurrencySymbol(row?.original?.amount_currency || "$")}${(row?.original?.total / 100).toFixed(2)}`,
        },
        {
            header: 'Status',
            accessorKey: 'status',
            cell: ({ row }) => {
                return (
                    <span className={`text-font-14 font-semibold ${row.original.status === 'paid' ? 'text-green' : 'text-red'}`}>
                        {row.original.status.toUpperCase()}
                    </span>
                );
            },
        },
        {
            header: 'Action',
            accessorKey: 'action',
            cell: ({ row }) => {
                const invoiceUrl = row.original.invoice_pdf;
                return (
                    <div className="flex flex-col items-end">
                       <span 
                            className="text-font-14 font-semibold text-blue cursor-pointer"
                            onClick={() => handleDownload(invoiceUrl)}
                        >
                            Download
                        </span>
                    </div>
                );
            },
        }
    ];

    const table = useReactTable({
        data: invoiceList?.data || [],
        columns,
        state: {
            sorting,
            columnFilters,
            pagination,
        },
        pageCount: Math.ceil(totalRecords / pagination.pageSize),
        manualPagination: true,
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onPaginationChange: setPagination,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
    });
    
    return (
        <>
            {/* <div className="flex gap-5 mb-6 mt-3">
                <div className="border border-b10 rounded-10 p-5 flex-1">
                    <p className="text-font-14 text-b6 mb-2.5">
                        Next Invoice Issue Date
                    </p>
                    <h5 className="text-font-18 text-b2 font-semibold">
                        Apr 13, 2024
                    </h5>
                </div>
                <div className="border border-b10 rounded-10 p-5 flex-1">
                    <p className="text-font-14 text-b6 mb-2.5">
                        Current Subscription
                    </p>
                    <h5 className="text-font-18 text-b2 font-semibold">
                        Weam Plus
                    </h5>
                </div>
                <div className="border border-b10 rounded-10 p-5 flex-1">
                    <p className="text-font-14 text-b6 mb-2.5">
                        Invoice Total
                    </p>
                    <h5 className="text-font-18 text-b2 font-semibold">
                        $95
                    </h5>
                </div>
            </div> */}
            <div className="flex flex-col w-full">
                <div className="flex items-center justify-between mb-5">
                    <DataTableSearch
                        placeholder={'Search Invoice'}
                        handleFilterChange={handleFilterChange}
                        value={filterInput ?? ''}
                    />
                    <div className="flex space-x-2">
                        <DataTablePageSizeSelector
                            pagination={pagination}
                            handlePageSizeChange={handlePageSizeChange}
                        />
                    </div>
                </div>
                <Datatable table={table} loading={loading} />
                <DataTablePagination
                    table={table}
                    pagination={pagination}
                    handlePageSizeChange={handlePageSizeChange}
                />
            </div>
        </>
    );
};

export default InvoiceList; 