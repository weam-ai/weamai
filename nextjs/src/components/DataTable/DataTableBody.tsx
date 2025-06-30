
import React from 'react';
import { TableBody, TableRow, TableCell } from '@/components/ui/table';
import { flexRender } from '@tanstack/react-table';

export default function DataTableBody({ rows, columns,loading }) {
  return (
<TableBody>
  {loading ? (
    <TableRow>
      <TableCell colSpan={columns.length} align="center">
        <div className="flex justify-center items-center h-full mt-5 mb-5">
          <div className="dot-flashing"></div>
        </div>
      </TableCell>
    </TableRow>
  ) : rows?.length > 0 ? (
    rows.map((row) => (
      <TableRow key={row.id}>
        {row.getVisibleCells().map((cell) => (
          <TableCell key={cell.id}>
            {flexRender(cell.column.columnDef.cell, cell.getContext())}
          </TableCell>
        ))}
      </TableRow>
    ))
  ) : (
    <TableRow>
      <TableCell colSpan={columns.length} className="h-24 text-center">
        No Result Found
      </TableCell>
    </TableRow>
  )}
</TableBody>

  );
}