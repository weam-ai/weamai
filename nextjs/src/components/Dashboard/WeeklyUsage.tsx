import React, { useEffect, useState } from 'react';
import Datatable from '@/components/DataTable/DataTable';
import {
    useReactTable,
    getCoreRowModel,
    getFilteredRowModel,
    getPaginationRowModel,
} from '@tanstack/react-table';
import useUsage from '@/hooks/usage/useUsage';
import { dateDisplay } from '@/utils/common';
import DataTablePagination from '../DataTable/DataTablePagination';

const WeeklyUsage = ({ searchValue, pagination, setPagination, exportCode, setSelectExportCode, startDate, endDate, planCode }) => {
    const { getWeeklyUsage, userList, totalRecords, loading, weeksName, exportLoading } = useUsage();
    const [sorting, setSorting] = useState([]);
    const columns = [
        {
          accessorKey: 'companyNm',
          header: 'Company',
          enableSorting: false  
        },
        {
          accessorKey: 'username',
          header: 'Name',
          enableSorting: false
        },
        {
          accessorKey: 'email',
          header: 'Email',
          enableSorting: false
        },        
        {
          accessorKey: 'createdAt',
          header: 'Created At',
          cell: ({row}) => dateDisplay(row?.original?.createdAt),
          enableSorting: false,
        },
        {
          accessorKey: 'countryName',
          header: 'Country',
          enableSorting: false
        },
        {
          accessorKey: 'totalMember',
          header: 'Members',
          enableSorting: false
        },
        ...weeksName
    ];

	const table = useReactTable({
        data: userList,
        columns,
        pageCount: Math.ceil(totalRecords / pagination.pageSize),
        state: {
            sorting,
            pagination,
        },
        getCoreRowModel: getCoreRowModel(),
        manualPagination: true,
		    manualSorting: true,
        onSortingChange: (newSorting) => {
          setSorting(newSorting);          
        },
        onPaginationChange: setPagination,
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
    });

    useEffect(() => {
        getWeeklyUsage(pagination.pageSize, pagination.pageIndex * pagination.pageSize, searchValue, sorting, exportCode, startDate, endDate, planCode);        
  }, [pagination, searchValue, sorting, startDate, endDate, planCode]);

	useEffect(() => {
		if(exportCode?.length > 0){
			getWeeklyUsage(pagination.pageSize, pagination.pageIndex * pagination.pageSize, searchValue, sorting, exportCode, startDate, endDate, planCode);
			setSelectExportCode('');
		}		
	}, [exportCode]);

    const tableSortingClm = table.getState().sorting[0];
	const sortingColumn = tableSortingClm ? 
			{ [tableSortingClm.id]: tableSortingClm.desc ? -1 : 1 } 
			: {};

    const handlePageSizeChange = (pageSize) => {
    	setPagination((old) => ({ ...old, pageSize }));
    };

    useEffect(() => {
		const fetchData = () => {
            const tableSortingClm = table.getState().sorting[0];
            const sortingColumn = tableSortingClm ? 
                { [tableSortingClm.id]: tableSortingClm.desc ? -1 : 1 } 
                : {};
            const offset = searchValue?.length > 0 ? 0 : pagination.pageIndex * pagination.pageSize
			getWeeklyUsage(pagination.pageSize, offset, searchValue, sorting, exportCode, startDate, endDate, planCode);
		};
		const timer = setTimeout(fetchData, 1000);
		return () => clearTimeout(timer);
    }, [searchValue]);

    return (
        <div className='overflow-x-auto max-w-[100vw]'>
			  {exportLoading && 'Exporting Data...'} 
            <Datatable table={table} loading={loading} />
            <div className='flex justify-between items-center'>
              <div className=''>Total Companies: {totalRecords}</div>
              <DataTablePagination
                  table={table}
                  pagination={pagination}
                  handlePageSizeChange={handlePageSizeChange}
              />
            </div>
        </div>
    );
};
 
export default WeeklyUsage;