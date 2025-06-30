'use client';
import React, { useState, useEffect } from 'react';
import useModal from '@/hooks/common/useModal';
import useUsers from '@/hooks/users/useUsers';
import { ROLE_TYPE, USER_STATUS } from '@/utils/constant';
import { dateDisplay } from '@/utils/common';
import RemoveIcon from '@/icons/RemoveIcon';
import AlertDialogConfirmation from '@/components/AlertDialogConfirmation';
import ProfileImage from '@/components/Profile/ProfileImage';
import ToggleOn from '@/icons/ToggleOn';
import ToggleOff from '@/icons/ToggleOff';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { getCurrentUser } from '@/utils/handleAuth';
import DownArrowIcon from '@/icons/DownArrow';
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
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '@/components/ui/tooltip';

export const Member = ({ selectedTab, membersOptions, setTotalMembers, totalMembers }:any) => {
    const { getUsersList, users, totalRecords, removeUser, tableLoader } = useUsers();
    const { openModal, closeModal, isOpen: isConfirmOpen } = useModal();
    const currLoggedInUser=getCurrentUser()

    const [columnFilters, setColumnFilters] = useState([]);
    const [sorting, setSorting] = useState([]);
    const [filterInput, setFilterInput] = useState('');
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });
    const [deluser, setDeluser] = useState('');
    const requestSize = false;
    
    const handleUserDelete = (id) => {
        removeUser(deluser);
        closeModal();
        setDeluser('');
        setTotalMembers(totalMembers - 1);
    }

    const handleFilterChange = (e) => {
        const value = e.target.value || '';
        setColumnFilters((old) => [
            {
                id: 'user',
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
            getUsersList([USER_STATUS.ACCEPT], requestSize, filterInput, pagination.pageSize, (pagination.pageIndex) * pagination.pageSize);

        },500)

        return () => clearTimeout(timer)

    }, [pagination, filterInput, sorting, columnFilters]);


    useEffect(() => {
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    }, [selectedTab,filterInput]);
    
    useEffect(() => {
        setTotalMembers(totalRecords);
    }, [totalRecords]);

    let columns = [
        {
            header: 'User',
            accessorKey:'email',
            cell: ({row}) => ( <span className="inline-flex space-x-2.5">
                <ProfileImage user={row.original} w={40} h={40} 
                    classname={'user-img size-10 rounded-full mr-2.5 object-cover'}
                    spanclass={'user-char flex items-center justify-center size-[35px] rounded-full bg-[#B3261E] text-b15 text-font-16 font-normal mr-2.5'}  />
                <span className="flex flex-col">
                    <span className="text-font-14 font-semibold text-b2">
                        {row.getValue("email")}
                    </span>
                    <span className="text-font-12 font-b5 font-normal">
                    {row?.original?.fname && row?.original?.lname && row?.original?.fname + " " +row?.original?.lname}
                    </span>
                </span>
            </span>),
        },
        {
            header: 'Joined',
            accessorKey: 'joined',
            cell: ({row}) => dateDisplay(row?.original?.createdAt),
        },
        {
            header: 'Role',
            accessorKey: 'role',
            cell: ({row}) => row?.original?.roleCode            
        },        
        {
            header: '',
            accessorKey: 'action',
            cell: ({row}) => {
                const visibilityAction =
                    (currLoggedInUser.roleCode === ROLE_TYPE.COMPANY_MANAGER &&
                        row?.original?.roleCode === ROLE_TYPE.COMPANY_MANAGER) ||
                    (currLoggedInUser.roleCode === ROLE_TYPE.COMPANY_MANAGER &&
                        row?.original?.roleCode === ROLE_TYPE.COMPANY) ||
                    row?.original?.roleCode === ROLE_TYPE.COMPANY;

                return (
                    <button
                        key={row?.original?._id}
                        style={{
                            visibility: `${
                                visibilityAction ? 'hidden' : 'visible'
                            }`,
                        }}
                        disabled={visibilityAction}
                        onClick={() => {
                            openModal();
                            setDeluser(row?.original?.id);
                        }}
                    >
                        <TooltipProvider
                            delayDuration={0}
                            skipDelayDuration={0}
                        >
                            <Tooltip>
                                <TooltipTrigger>
                                    <RemoveIcon
                                        className={
                                            'w-4 h-4 fill-b4 hover:fill-red object-contain'
                                        }
                                        width={16}
                                        height={16}
                                    />
                                </TooltipTrigger>
                                <TooltipContent side="top">
                                    <p>Remove member</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                    </button>
                );
            }
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
    }, [selectedTab, filterInput]);

    return (
        <>
            <div className="flex flex-col w-full">
                <div className="flex md:items-center justify-between mb-5 md:flex-row flex-col">
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

            {isConfirmOpen && (
                <AlertDialogConfirmation
                    description={'Are you sure you want to delete?'}
                    btntext={'Delete'}
                    btnclassName={'btn-red'}
                    open={openModal}
                    closeModal={closeModal}
                    handleDelete={handleUserDelete}
                    id={deluser}
                />
            )}
        </>
    );
}