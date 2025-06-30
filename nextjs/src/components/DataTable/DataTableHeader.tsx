import React from 'react';
import { TableHeader, TableRow, TableHead } from '@/components/ui/table';
import { flexRender } from '@tanstack/react-table';
import AscendingIcon from '@/icons/AscendingIcon';
import DescendingIcon from '@/icons/DescendingIcon';

export default function DatatableHeader({ headerGroups }) {
  return (
    <TableHeader>
      {headerGroups.map(headerGroup => (
        <TableRow key={headerGroup.id}>
          {headerGroup.headers.map(header => (
            <TableHead key={header.id}>
              {header.isPlaceholder ? null : (
                <div
                  className={
                    header.column.getCanSort()
                      ? 'cursor-pointer select-none flex items-center w-full justify-center'
                      : ''
                  }
                  onClick={header.column.getToggleSortingHandler()}
                  // title={
                  //   header.column.getCanSort()
                  //     ? header.column.getNextSortingOrder() === 'asc'
                  //       ? 'Sort ascending'
                  //       : header.column.getNextSortingOrder() === 'desc'
                  //         ? 'Sort descending'
                  //         : 'Clear sort'
                  //     : undefined
                  // }
                >
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}
                  {header.column.getCanSort() && (
                    <>
                      {header.column.getIsSorted() === "asc" && <AscendingIcon className="w-1.5 h-auto ml-1 fill-b9 mt-1" />}
                      {header.column.getIsSorted() === "desc" && <DescendingIcon className="w-1.5 h-auto ml-1 fill-b9 mt-1" />}
                    </>
                  )}
                </div>
              )}
              {/* {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())} */}
            </TableHead>
          ))}
        </TableRow>
      ))}
    </TableHeader>
  );
}