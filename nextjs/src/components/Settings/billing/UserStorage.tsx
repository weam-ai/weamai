import React, { useEffect, useState } from 'react';
import DoughnutChartBilling from '@/components/Settings/DoughnutChartBilling';
import useBilling from '@/hooks/billing/useBilling';
import { bytesToMegabytes, dateDisplay } from '@/utils/common';
import ProfileImage from '@/components/Profile/ProfileImage';
import {
    useReactTable,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
    getSortedRowModel,
} from '@tanstack/react-table';
import Datatable from '@/components/DataTable/DataTable';
import DataTablePagination from '@/components/DataTable/DataTablePagination';
import DataTablePageSizeSelector from '@/components/DataTable/DataTablePageSizeSelector';
import DataTableSearch from '@/components/DataTable/DataTableSearch';


const UserStorage = () => {

    const { getUserStorage, users, totalPages, totalRecords, tableLoader } = useBilling();

    const [columnFilters, setColumnFilters] = useState([]);
    const [sorting, setSorting] = useState([]);
    const [filterInput, setFilterInput] = useState('');
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });
    const requestSize = false;

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

        const timer=setTimeout(()=>{

            getUserStorage(requestSize, filterInput, pagination.pageSize, (pagination.pageIndex) * pagination.pageSize);
        },500)

        return ()=> clearTimeout(timer)
    }, [pagination, filterInput, sorting, columnFilters]);

    let columns = [
        {
            header: 'Name',
            accessorKey: 'email',
            cell: ({row}) => <span className="inline-flex space-x-2.5 items-center">
                {/* <span className="bg-reddark text-b15 w-10 h-10 min-w-10 rounded-full flex items-center justify-center text-font-20 font-normal">
                    {getEmailFirstLetter(row?.email)}
                </span> */}
                <ProfileImage user={row.original} w={40} h={40} 
                    classname={'user-img size-10 rounded-full mr-2.5 object-cover'}
                    spanclass={'user-char flex items-center justify-center size-[35px] rounded-full bg-[#B3261E] text-b15 text-font-16 font-normal mr-2.5'}  />
                <span className="flex flex-col">
                    <span className="text-font-14 font-semibold text-b2">
                        {row?.original?.email}
                    </span>
                    <span className="text-font-12 font-b5 font-normal">
                        {row?.original?.fname && row?.original?.lname && row?.original?.fname + " " +row?.original?.lname}
                    </span>
                </span>
            </span>
        },
        {
            header: 'Date',
            accessorKey: 'date',
            cell: ({row}) => dateDisplay(row?.original?.createdAt),
        },
        {
            header: 'Workspaces',
            accessorKey: 'workspaces',
            cell: ({row}) => row?.original?.totalWorkspace,
        },
        {
            header: 'Brains',
            accessorKey: 'brains',
            cell: ({row}) => row?.original?.totalBrain,
        },
        {
            header: 'Storage',
            accessorKey: 'storage',
            cell: ({ row }) => (
                <div className="relative overflow-hidden h-12 flex items-center justify-center scale-95 transform-origin-center">
                    <DoughnutChartBilling
                        value={bytesToMegabytes(row?.original?.usedSize)}
                        maxValue={bytesToMegabytes(row?.original?.fileSize)}
                    />
                </div>
            ),
        }
    ];

    const table = useReactTable({
        data: users,
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


    useEffect(() => {
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    }, [ filterInput]);

    return (
        <div className="flex flex-col w-full">
            <div className="flex items-center justify-between mb-5">
                <DataTableSearch
                    placeholder={'Search a Member'}
                    handleFilterChange={handleFilterChange}
                    value={filterInput ?? ''}
                />
                <div className="flex space-x-2">
                    <DataTablePageSizeSelector
                        pagination={pagination}
                        handlePageSizeChange={handlePageSizeChange}
                    />
                    {/* <button className="ml-auto btn btn-outline-gray">
                            Export Data
                        </button> */}
                </div>
            </div>
            <Datatable table={table} loading={tableLoader} />
            <DataTablePagination
                table={table}
                pagination={pagination}
                handlePageSizeChange={handlePageSizeChange}
            />
        </div>
    );
};

export default UserStorage;
