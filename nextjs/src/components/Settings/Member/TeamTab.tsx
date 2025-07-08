import React, { useState, useEffect } from 'react';

import RemoveIcon from '@/icons/RemoveIcon';
import AlertDialogConfirmation from '@/components/AlertDialogConfirmation';
import EditIcon from '@/icons/Edit';

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
import { useTeams } from '@/hooks/team/useTeams';
import TeamModal from './TeamModal';
import { useSelector } from 'react-redux';
import { RootState } from '@/lib/store';
import { deleteTeamAction } from '@/actions/team';
import useServerAction from '@/hooks/common/useServerActions';
import { removeObjectFromArray } from '@/utils/common';
import Toast from '@/utils/toast';

const TeamTab = ({ selectedTab, setTotalTeam, totalTeam }) => {
    const [columnFilters, setColumnFilters] = useState([]);
    const [sorting, setSorting] = useState([]);
    const [filterInput, setFilterInput] = useState('');
    const [pagination, setPagination] = useState({
        pageIndex: 0,
        pageSize: 10,
    });
    const [openEditModal, setOpenEditModal] = useState(false);
    const [openAddModal, setOpenAddModal] = useState(false);
    const [opendeleteModal, setOpenDeleteModal] = useState(false);
    const [selectedTeam, setSelectedTeam] = useState({});
    const [deleteTeam,isDeleteTeamPending] = useServerAction(deleteTeamAction)
    const allWorkspaceList=useSelector((state:RootState)=>state.workspacelist.list).map((curr)=>curr._id)

    const {
        createTeam,
        getTeams,
        updateTeam,
        // deleteTeam,
        teams,
        setTeams,
        watch,
        setFormValue,
        control,
        errors,
        clearErrors,
        handleSubmit,
        loading: teamLoading,
        register,
        isDirty,
        reset,
        totalRecords:totalTeams,
        setTotalRecords
    } = useTeams();

    const columns = [
        {
            header: ({ column }) => (
                <button
                    className="inline-flex items-center justify-center whitespace-nowrap outline-none"
                    onClick={() =>
                        column.toggleSorting(column.getIsSorted() === 'asc')
                    }
                >
                    Teams
                    <UpDownArrowIcon
                        width={'15'}
                        height={'15'}
                        className="ml-1 size-[15px] fill-b5"
                    />
                </button>
            ),
            accessorKey: 'teamName',
            cell: ({ row }) => {
                return (
                    <span className="inline-flex space-x-2.5">
                        <span className="flex flex-col">
                            <span className="text-font-14 font-semibold text-b2">
                                {row.getValue('teamName')}
                            </span>
                            {/* <span className="text-font-12 font-b5 font-normal">
                                {row?.original?.fname &&
                                    row?.original?.lname &&
                                    row?.original?.fname +
                                        ' ' +
                                        row?.original?.lname}
                            </span> */}
                        </span>
                    </span>
                );
            },
        },
        {
            header:"No. of members",
            accessorKey:'',
            cell: ({row})=>{
                return <span> {row.original.teamUsers.length} </span>
            }
        },
        {
            header: 'Edit',
            accessorKey: 'edit_action',
            cell: ({ row }) => (
                <button
                    onClick={() => {
                        setOpenEditModal(true);
                        setSelectedTeam(row.original);
                    }}
                >
                    <EditIcon
                        className="w-4 h-4 fill-b4 hover:fill-red object-contain"
                        width={16}
                        height={16}
                    />
                </button>
            ),
        },
        {
            header: 'Delete',
            id: 'delete_action',
            cell: ({ row }) => (
                <button
                    onClick={() => {
                        setOpenDeleteModal(true);
                        setSelectedTeam({ _id: row.original?._id });
                       
                    }}
                >
                    <RemoveIcon
                        className="w-4 h-4 fill-b4 hover:fill-red object-contain"
                        width={16}
                        height={16}
                    />
                </button>
            ),
        },
    ];

    const table = useReactTable({
        data: teams,
        columns,
        state: {
            sorting,
            columnFilters,
            pagination,
        },
        pageCount: Math.ceil(totalTeams / pagination.pageSize),
        manualPagination: true,
        onSortingChange: setSorting,
        onColumnFiltersChange: setColumnFilters,
        onPaginationChange: setPagination,
        getCoreRowModel: getCoreRowModel(),
        getFilteredRowModel: getFilteredRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        getSortedRowModel: getSortedRowModel(),
        enableSorting: false
    });

    const handleFilterChange = (e) => {
        const value = e.target.value || '';
        // setColumnFilters((old) => [
        //     {
        //         id: 'teamName',
        //         value: value?.toLowerCase(),
        //     },
        // ]);
        setFilterInput(value);
    };

    const handlePageSizeChange = (pageSize) => {
        setPagination((old) => ({ ...old, pageSize }));
    };

    const handleTeamDelete = async (id) => {
        const response = await deleteTeam(id,allWorkspaceList);
        const updatedObj = removeObjectFromArray(teams, id);
        setTeams(updatedObj || []);
        setTotalRecords((prev)=>prev-1)
        Toast(response.message);
        setOpenDeleteModal(false);
    };

    useEffect(() => {
        setPagination((prev) => ({ ...prev, pageIndex: 0 }));
    }, [selectedTab,filterInput]);

    useEffect(() => {
        const handler = setTimeout(() => {
            getTeams({
                search: filterInput,
                pagination: true,
                limit: pagination.pageSize,
                offset: pagination.pageIndex * pagination.pageSize,
                sort: sorting,
                sortby: columnFilters,
            })
    
            
        }, 500);
    
        return () => {
            clearTimeout(handler);
        };
    }, [pagination, filterInput, sorting, columnFilters]);

    useEffect(()=>{
        setTotalTeam(totalTeams)
    },[totalTeams])

    return (
        <>
            {/* Add Team modal start */}
            <TeamModal
                register={register}
                errors={errors}
                control={control}
                handleSubmit={handleSubmit}
                watch={watch}
                setFormValue={setFormValue}
                createTeam={createTeam}
                openAdd={() => {
                    reset();
                    setOpenAddModal(true);
                }}
                closeAdd={() => {
                    reset();
                    setOpenAddModal(false);
                }}
                addModal={openAddModal}
                isDirty={isDirty}
                reset={reset}
                clearErrors={clearErrors}
                setTeams={setTeams}
            />
            {/* Add Team modal end */}

            <div className="flex flex-col w-full">
                <div className="flex items-center justify-between mb-5">
                    <DataTableSearch
                        placeholder={'Search a Team Name'}
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
                <Datatable table={table} loading={teamLoading} />
                <DataTablePagination
                    table={table}
                    pagination={pagination}
                    handlePageSizeChange={handlePageSizeChange}
                />
            </div>

            {opendeleteModal && (
                <AlertDialogConfirmation
                    description={'Are you sure you want to delete?'}
                    btntext={'Delete'}
                    btnclassName={'btn-red'}
                    open={opendeleteModal}
                    closeModal={() => setOpenDeleteModal(false)}
                    handleDelete={handleTeamDelete}
                    id={selectedTeam._id}
                    loading={isDeleteTeamPending}
                />
            )}

            {openEditModal && (
                <TeamModal
                    register={register}
                    errors={errors}
                    control={control}
                    handleSubmit={handleSubmit}
                    watch={watch}
                    setFormValue={setFormValue}
                    updateTeam={updateTeam}
                    team={selectedTeam}
                    isEdit={true}
                    closeEdit={() => {
                        reset();
                        setOpenEditModal(false);
                    }}
                    isDirty={isDirty}
                    teamLoading={teamLoading}
                    reset={reset}
                    clearErrors={clearErrors}
                    setTeams={setTeams}
                />
            )}
        </>
    );
};

export default TeamTab;
