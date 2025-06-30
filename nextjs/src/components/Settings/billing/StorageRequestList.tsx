'use client';
import React, { useState, useEffect } from 'react';
import {
    useReactTable,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
} from '@tanstack/react-table';
import { PAGINATION } from '@/utils/constant';
import RequestDetailsModal from '@/components/Settings/RequestDetailsModal';
import DataTableSearch from '@/components/DataTable/DataTableSearch';
import DataTablePageSizeSelector from '@/components/DataTable/DataTablePageSizeSelector';
import Datatable from '@/components/DataTable/DataTable';
import DataTablePagination from '@/components/DataTable/DataTablePagination';
import useStorage from '@/hooks/storage/useStorage';
import ProfileImage from '@/components/Profile/ProfileImage';
import { bytesToMegabytes } from '@/utils/common';
import { STORAGE_REQUEST_STATUS } from '@/utils/constant';

const StorageRequestList = ({ selectedTab }:any) => {
    const [searchFilter, setSearchFilter] = useState('');
    const [sortby, setSortBy] = useState('id');
    const [sort, setSort] = useState(PAGINATION.SORTING);
    const [perPageSize, setPerPageSize] = useState(PAGINATION.PER_PAGE_RECORD);
    const [page, setPage] = useState(1);
    const [columnFilters, setColumnFilters] = useState([]);
    const [sorting, setSorting] = useState([]);
    const [filterInput, setFilterInput] = useState('');
    const [isRequestSizeModalOpen, setRequestSizeModalOpen] = useState(false);
    const [selectedRequest, setSelectedRequest] = useState(null);
    const [refreshStorageRequests, setRefreshStorageRequests] = useState(false);
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });    
    
    const { 
        getPendingStorageRequest, storageRequestList, loading, totalRecords
    } = useStorage();

    const openRequestSizeModal = (request) => {
        setSelectedRequest(request);
        setRequestSizeModalOpen(true);
    };

    const closeRequestSizeModal = () => {
        setRequestSizeModalOpen(false);
    };

    useEffect(() => {
        getPendingStorageRequest(STORAGE_REQUEST_STATUS.PENDING, searchFilter, perPageSize, (page - 1) * perPageSize, sort, sortby);                
    }, [sort, sortby, page, perPageSize, searchFilter, refreshStorageRequests]);

    useEffect(() => {
        setPage(1);
    }, [selectedTab]);

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
    }, [selectedTab,filterInput]);        

    const columns = [
        {
            header: 'Name',
            accessorKey: 'email',
            cell: ({row}) => <span className="inline-flex space-x-2.5">
                <ProfileImage user={row.original?.user} w={40} h={40} 
                    classname={'user-img size-10 rounded-full mr-2.5 object-cover'}
                    spanclass={'user-char flex items-center justify-center size-[35px] rounded-full bg-[#B3261E] text-b15 text-font-16 font-normal mr-2.5'}  />
                <span className="flex flex-col">
                    <span className="text-font-14 font-semibold text-b2">
                        {row?.original?.user?.email}
                    </span>
                    <span className="text-font-12 font-b5 font-normal">
                        {row?.original?.user?.fname}
                    </span>
                </span>
            </span>,
        },
        {
            header: 'Requested for',
            accessorKey: 'requestSize',
            cell: ({row}) => {
                return <>Increase Storage by {' '}
                    <span className="text-b2 font-semibold">
                        {bytesToMegabytes(row?.original?.requestSize)} {'mb'}
                    </span></>;
            },
        },
        {
            header: '',
            accessorKey: 'action',
            cell: ({row}) => <div className="flex items-center">
                <button
                    type="button"
                    className="btn btn-outline-gray"
                    onClick={() => openRequestSizeModal(row?.original)}
                >
                    Approve / Decline
                </button>
                {/* <button
                    type="button"
                    onClick={handleOpen}
                    className="ms-3 transparent-ghost-btn btn-round btn-round-icon [&>svg>path]:fill-b5"
                >
                    <RightArrow />
                </button> */}
            </div>
        }
    ];

    const table = useReactTable({
        data: storageRequestList || [],
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
            <div className="flex flex-col w-full">
                <div className="flex items-center justify-between mb-5">
                    <DataTableSearch
                        placeholder={'Search a Member Name'}
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

            {isRequestSizeModalOpen && (
                <RequestDetailsModal 
                    closeModal={closeRequestSizeModal}
                    selectedRequest={selectedRequest}
                    setRefreshStorageRequests={setRefreshStorageRequests}
                    refreshStorageRequests={refreshStorageRequests}
                />
            )}            
        </>
    );
};

export default StorageRequestList; 