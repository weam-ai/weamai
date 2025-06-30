import { PaginatorType } from '@/types/common';
import React from 'react';

type PaginationControlProps = {
    isLoading: boolean;
    paginator: PaginatorType;
    handlePagination: (type: 'next' | 'previous') => void;
};

type LoadMorePaginationProps = PaginationControlProps & {
    handlePagination: () => void;
}

const PaginationControl = ({ isLoading, paginator, handlePagination }: PaginationControlProps) => {
    return (
        <div className='flex justify-between max-w-[950px] mx-auto'>
            {!isLoading && paginator?.hasPrevPage && (
                <div className="load-more-btn text-left px-5 mt-[30px]">
                    <button
                        className="btn btn-outline-black"
                        onClick={() => handlePagination('previous')}
                        disabled={isLoading}
                    >
                        Previous
                    </button>
                </div>
            )}
            {!isLoading && paginator?.hasNextPage && (
                <div className="load-more-btn text-right px-5 mt-[30px] flex-1">
                    <button
                        className="btn btn-outline-black"
                        onClick={() => handlePagination('next')}
                        disabled={isLoading}
                    >
                        Next
                    </button>
                </div>
            )} 
        </div>
    );
};

export const LoadMorePagination = ({ isLoading, handlePagination, paginator }: LoadMorePaginationProps) => {
    return (
        <>
            {
                !isLoading && paginator?.hasNextPage && (
                    <div className="load-more-btn text-center px-5 mt-[30px]">
                        <button className="btn btn-outline-black" onClick={() => handlePagination()} disabled={isLoading}>Load More</button>
                    </div>
                )
            }
        </>
    )
}

export default PaginationControl;
