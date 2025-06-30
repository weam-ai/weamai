import commonApi from '@/api';
import { useState } from 'react';
import { MODULE_ACTIONS, DEFAULT_SORT } from '@/utils/constant';
import jsonToCsvExport from 'json-to-csv-export';
const useUsage = () => {
    const [loading, setLoading] = useState(false);
    const [exportLoading, setExportLoading] = useState(false);
    const [userList, setUserList] = useState([]);
    const [totalRecords, setTotalRecords] = useState(0);
    const [totalPages, setTotalPages] = useState(0);
    const [weeksName, setWeeksName] = useState([]);
    
    const getUsage = async (limit, offset, model, startDate, endDate, searchValue='', sortingColumn={}, isPaid) => {
        (Object.keys(sortingColumn).length === 0) ? 
            sortingColumn = {msgCount: DEFAULT_SORT} : sortingColumn;

        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.GET_USAGE,
                data: {
                    options: {
                        offset: offset,
                        limit: limit,
                        sort: sortingColumn
                    },
                    query: {
                        search: searchValue,
                    },
                    modelCode: model,
                    startDate: startDate,
                    endDate: endDate,
                    isPaid: isPaid
                },
            });
            setUserList(response.data);
            setTotalRecords(response?.paginator?.itemCount || 0);
            setTotalPages(response?.paginator?.pageCount);
        } catch (error) {
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const getUserUsage = async (limit, offset, model, startDate, endDate, sortingColumn, isPaid) => {
        try {
            setLoading(true);
            (Object.keys(sortingColumn).length === 0) ? 
                sortingColumn = {msgCount: DEFAULT_SORT} : sortingColumn;

            const response = await commonApi({
                action: MODULE_ACTIONS.GET_USER_USAGE,
                data: {
                    options: {
                        offset: offset,
                        limit: limit,
                        sort: sortingColumn,
                    },
                    query: {
                        search: '',
                    },
                    modelCode: model,
                    startDate: startDate,
                    endDate: endDate,
                    isPaid: isPaid
                },
            });
            setUserList(response.data);
            setTotalRecords(response?.paginator?.itemCount || 0);
            setTotalPages(response?.paginator?.pageCount);
        } catch (error) {
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const getWeeklyUsage = async (limit, offset, searchValue='', sortingColumn={}, exportCode, startDate, endDate, planCode) => {
        (Object.keys(sortingColumn).length === 0) ? 
            sortingColumn = {msgCount: DEFAULT_SORT} : sortingColumn;

        try {
            (!exportCode) ? setLoading(true) : setExportLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.GET_WEEKLY_USAGE,
                data: {
                    options: {
                        offset: offset,
                        limit: limit,
                        sort: sortingColumn
                    },
                    query: {
                        search: searchValue,
                    },
                    exportCode: exportCode,
                    startDate: startDate,
                    endDate: endDate,
                    planCode: planCode
                },
            });
            
            if(!exportCode){
                setUserList(response.data?.msgCountResult);
                setWeeksName(response.data?.weeklyDateRanges);
                setTotalRecords(response?.paginator?.itemCount || 0);
                setTotalPages(response?.paginator?.pageCount);
            } else {
                exportToCsv(response.data?.msgCountResult);
            }
        } catch (error) {
            throw error;
        } finally {
            setLoading(false);
            setExportLoading(false);
        }
    };

    const exportToCsv = (usageData) => {
        const currentDate = new Date();
        const formattedDate = currentDate.toISOString().split('T')[0]; // Format as YYYY-MM-DD

        jsonToCsvExport({ data: usageData, filename: `${formattedDate}-weekly-usage-report.csv` });
    }

    return {
        loading,
        getUsage,
        userList,
        totalRecords,
        totalPages,
        getUserUsage,
        weeksName,
        getWeeklyUsage,
        exportLoading
    };
};

export default useUsage;