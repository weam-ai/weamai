import React, { useState } from 'react';
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
import UpDownArrowIcon from '@/icons/UpDownArrowIcon';
import EditIcon from '@/icons/Edit';
import StorageSelector from '../StorageSelector';
import userPlaceholder from '../../../public/user-placeholderlight.jpg'
import Image from 'next/image';

const handleEdit = (rowData) => {
    // Your edit handler logic
};

const data = [
    {
        srNo: '01',
        userName: 'Willian Iralzabal',
        email: 'willianiralzabalt@brightHorizonsolutions.com',
        dateJoined: '04/17/2024',
        assignedStorage: '50',
        role: 'Admin',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '02',
        userName: 'John Doe',
        email: 'john.doe@example.com',
        dateJoined: '05/12/2024',
        assignedStorage: '30',
        role: 'User',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '03',
        userName: 'Jane Smith',
        email: 'jane.smith@example.com',
        dateJoined: '06/15/2024',
        assignedStorage: '70',
        role: 'Admin',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '04',
        userName: 'Alice Johnson',
        email: 'alice.johnson@example.com',
        dateJoined: '07/21/2024',
        assignedStorage: '40',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '05',
        userName: 'Robert Brown',
        email: 'robert.brown@example.com',
        dateJoined: '08/09/2024',
        assignedStorage: '60',
        role: 'Admin',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '06',
        userName: 'Emily Davis',
        email: 'emily.davis@example.com',
        dateJoined: '09/01/2024',
        assignedStorage: '45',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '07',
        userName: 'Michael Wilson',
        email: 'michael.wilson@example.com',
        dateJoined: '10/11/2024',
        assignedStorage: '35',
        role: 'User',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '08',
        userName: 'Jessica Moore',
        email: 'jessica.moore@example.com',
        dateJoined: '11/22/2024',
        assignedStorage: '55',
        role: 'Admin',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '09',
        userName: 'David Taylor',
        email: 'david.taylor@example.com',
        dateJoined: '12/05/2024',
        assignedStorage: '65',
        role: 'User',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '10',
        userName: 'Sarah Anderson',
        email: 'sarah.anderson@example.com',
        dateJoined: '01/14/2024',
        assignedStorage: '50',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '11',
        userName: 'Thomas Thompson',
        email: 'thomas.thompson@example.com',
        dateJoined: '02/28/2024',
        assignedStorage: '40',
        role: 'Admin',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '12',
        userName: 'Nancy Martinez',
        email: 'nancy.martinez@example.com',
        dateJoined: '03/19/2024',
        assignedStorage: '30',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '13',
        userName: 'Christopher Garcia',
        email: 'christopher.garcia@example.com',
        dateJoined: '04/07/2024',
        assignedStorage: '60',
        role: 'Admin',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '14',
        userName: 'Karen Hernandez',
        email: 'karen.hernandez@example.com',
        dateJoined: '05/22/2024',
        assignedStorage: '45',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '15',
        userName: 'Mark Clark',
        email: 'mark.clark@example.com',
        dateJoined: '06/13/2024',
        assignedStorage: '55',
        role: 'User',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '16',
        userName: 'Patricia Lewis',
        email: 'patricia.lewis@example.com',
        dateJoined: '07/29/2024',
        assignedStorage: '65',
        role: 'Admin',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '17',
        userName: 'Kevin Walker',
        email: 'kevin.walker@example.com',
        dateJoined: '08/17/2024',
        assignedStorage: '40',
        role: 'User',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '18',
        userName: 'Donna Hall',
        email: 'donna.hall@example.com',
        dateJoined: '09/06/2024',
        assignedStorage: '50',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '19',
        userName: 'Paul King',
        email: 'paul.king@example.com',
        dateJoined: '10/18/2024',
        assignedStorage: '60',
        role: 'Admin',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '20',
        userName: 'Laura Wright',
        email: 'laura.wright@example.com',
        dateJoined: '11/01/2024',
        assignedStorage: '30',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '21',
        userName: 'Matthew Lopez',
        email: 'matthew.lopez@example.com',
        dateJoined: '12/12/2024',
        assignedStorage: '70',
        role: 'Admin',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '22',
        userName: 'Amy Scott',
        email: 'amy.scott@example.com',
        dateJoined: '01/23/2024',
        assignedStorage: '45',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '23',
        userName: 'Brian Green',
        email: 'brian.green@example.com',
        dateJoined: '02/05/2024',
        assignedStorage: '35',
        role: 'User',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '24',
        userName: 'Angela Adams',
        email: 'angela.adams@example.com',
        dateJoined: '03/30/2024',
        assignedStorage: '50',
        role: 'Admin',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '25',
        userName: 'George Baker',
        email: 'george.baker@example.com',
        dateJoined: '04/11/2024',
        assignedStorage: '60',
        role: 'User',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '26',
        userName: 'Heather Nelson',
        email: 'heather.nelson@example.com',
        dateJoined: '05/18/2024',
        assignedStorage: '40',
        role: 'Admin',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '27',
        userName: 'Jason Carter',
        email: 'jason.carter@example.com',
        dateJoined: '06/29/2024',
        assignedStorage: '45',
        role: 'User',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '28',
        userName: 'Stephanie Mitchell',
        email: 'stephanie.mitchell@example.com',
        dateJoined: '07/25/2024',
        assignedStorage: '55',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
    {
        srNo: '29',
        userName: 'Benjamin Perez',
        email: 'benjamin.perez@example.com',
        dateJoined: '08/15/2024',
        assignedStorage: '35',
        role: 'Admin',
        status: 'Deactivate',
        action: 'Edit',
    },
    {
        srNo: '30',
        userName: 'Megan Roberts',
        email: 'megan.roberts@example.com',
        dateJoined: '09/22/2024',
        assignedStorage: '70',
        role: 'User',
        status: 'Active',
        action: 'Edit',
    },
];

const columns = [
    {
        accessorKey: 'srNo',
        header: 'Sr.No',
    },
    {
        accessorKey: 'userName',
        header: 'User Name',
        cell: ({ getValue }) => (
            <div className="flex items-center">
                <Image width={30} height={30}
                    src={userPlaceholder}
                    alt={getValue()}
                    className="size-[30px] rounded-full mr-2.5"
                />
                {getValue()}
            </div>
        ),
    },
    {
        accessorKey: 'email',
        header: 'Email Address',
    },
    {
        accessorKey: 'dateJoined',
        header: ({ column }) => (
            <button
                className="inline-flex items-center justify-center whitespace-nowrap outline-none"
                onClick={() =>
                    column.toggleSorting(column.getIsSorted() === 'asc')
                }
            >
                Date Joined
                <UpDownArrowIcon
                    width={'15'}
                    height={'15'}
                    className="ml-1 size-[15px] fill-b5"
                />
            </button>
        ),
    },
    {
        accessorKey: 'assignedStorage',
        header: 'Assigned Storage',
        cell: () => (
            <StorageSelector />
        ),
    },
    {
        accessorKey: 'role',
        header: 'Role',
    },
    {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ getValue }) => (
            <span
                className={
                    getValue() === 'Active' ? 'text-green' : getValue() === 'Deactivate' ? 'text-reddark' : 'text-b2'
                }
            >
                {getValue()}
            </span>
        ),
    },
    {
        accessorKey: 'action',
        header: 'Action',
        cell: ({ row }) => (
            <button
                className="btn btn-lightblue p-[7px]"
                onClick={() => handleEdit(row.original)}
            >
                <EditIcon width={'14'} height={'14'} className={'size-3.5'} />
            </button>
        ),
    },
];


const CompanyListUserListTable = () => {
    const [columnFilters, setColumnFilters] = useState([]);
    const [sorting, setSorting] = useState([]);
    const [filterInput, setFilterInput] = useState('');
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });

    const handleFilterChange = e => {
        const value = e.target.value || '';
        setColumnFilters([{ id: 'userName', value }, { id: 'email', value }]);
        setFilterInput(value);
      };

    const handlePageSizeChange = (pageSize) => {
        setPagination((old) => ({ ...old, pageSize }));
    };

    const table = useReactTable({
        data,
        columns,
        state: {
            sorting,
            columnFilters,
            pagination,
        },
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onPaginationChange: setPagination,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
    });

    return (
        <div className="flex flex-col w-full">
            <div className="flex items-center justify-between mb-5">
             <DataTableSearch placeholder={"Search Member"}  handleFilterChange={handleFilterChange} value={filterInput}/>
                <div className="flex space-x-2">
                    <DataTablePageSizeSelector
                        pagination={pagination}
                        handlePageSizeChange={handlePageSizeChange}
                    />
                    <button className="ml-auto btn btn-outline-gray">
                        Export Data
                    </button>
                </div>
            </div>
            <Datatable table={table} />
            <DataTablePagination
                table={table}
                pagination={pagination}
                handlePageSizeChange={handlePageSizeChange}
            />
        </div>
    );
};

export default CompanyListUserListTable;
