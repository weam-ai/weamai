import React, { useState, useEffect } from 'react'

type UseSearchType = {
    func: (searchValue: string) => void;
    delay: number;
    dependency?: any[];
    resetState?: () => void;
}

const useSearch = ({ func, delay, dependency = [], resetState }: UseSearchType) => {

    const [searchValue, setSearchValue] = useState('');

    useEffect(() => {
        const fetchData = () => {
            resetState && resetState();
            func(searchValue)
        };
        const timer = setTimeout(fetchData, delay);
        return () => clearTimeout(timer);
    }, [searchValue, ...dependency]);

    return {
        searchValue,
        setSearchValue
    }
}

export default useSearch