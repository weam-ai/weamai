import React, { useState } from 'react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuRadioGroup,
    DropdownMenuRadioItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import FilterIcon from '@/icons/FilterIcon';

const RadioDropdown = ({ data, defaultValue }) => {
    const [position, setPosition] = useState(defaultValue);
    return (
        <DropdownMenu>
            <DropdownMenuTrigger className="absolute top-2 right-2.5 dropdown-action flex justify-center items-center w-[25px] h-[25px] min-w-[25px] rounded-full transition duration-150 ease-in-out outline-none">
                <FilterIcon
                    width={16}
                    height={16}
                    className="w-4 h-4 object-contain fill-b6"
                />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="min-w-[180px]">
                <DropdownMenuRadioGroup
                    value={position}
                    onValueChange={setPosition}
                >
                    {data.map((d) => (
                        <DropdownMenuRadioItem value={d.value} key={d.id}>
                            {d.value}
                        </DropdownMenuRadioItem>
                    ))}
                </DropdownMenuRadioGroup>
            </DropdownMenuContent>
        </DropdownMenu>
    );
};

export default RadioDropdown;
