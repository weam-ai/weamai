'use client';
import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import useDebounce from '@/hooks/common/useDebounce';
import routes from '@/utils/routes';
import CommonInput from '@/widgets/CommonInput';

const SearchInput = () => {
    const [searchValue, setSearchValue] = useState('');
    const [debouncedSearchValue] = useDebounce(searchValue, 300);
    const router = useRouter();
    const searchParams = useSearchParams();

    useEffect(() => {
        const params = new URLSearchParams(searchParams.toString());
        if (debouncedSearchValue.trim()) {
            params.set('query', debouncedSearchValue.trim());
            router.replace(`?${params.toString()}`);
        } else {
            params.delete('query');
            router.replace(routes.mcp);
        }
    }, [debouncedSearchValue]);

    return (
        <CommonInput
            type="text"
            className="default-form-input !pl-8"
            placeholder="Search"
            value={searchValue}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchValue(e.target.value)}
        />
    );
};

export default SearchInput;
