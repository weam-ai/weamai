import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import OptionsVerticalIcon from '@/icons/OptionsVerticalIcon';
import RemoveIcon from '@/icons/RemoveIcon';
import RenameIcon from '@/icons/RenameIcon';
import React from 'react';

const DropDownMenu = ({ flag = true, data, onEdit, onDelete }) => {
    const dropdown = [
        {
            id: 1,
            icon: (
                <RenameIcon 
                    width={14}
                    height={16}
                    className="w-[14] h-4 object-contain fill-b4 me-2.5"
                />
            ),
            text: 'Rename',
            action: onEdit
        },
        // {
        //     id: 2,
        //     icon: (
        //         <EditIcon
        //             width={14}
        //             height={16}
        //             className="w-[14] h-4 object-contain fill-b4 me-2.5"
        //         />
        //     ),
        //     text: 'Edit',
        // },
        {
            id: 3,
            icon: (
                <RemoveIcon
                    width={14}
                    height={16}
                    className="w-[14] h-4 object-contain fill-b4 me-2.5"
                />
            ),
            text: 'Delete',
            action: onDelete
        }
    ];
    return (
        <DropdownMenu>
            <DropdownMenuTrigger className="ml-auto dropdown-action transparent-ghost-btn btn-round btn-round-icon">
                <OptionsVerticalIcon />
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="min-w-[210px]">
                {dropdown.map((d) => (
                    <DropdownMenuItem key={d.id} onClick={d.action}>
                        {d.icon}
                        {d.text}
                    </DropdownMenuItem>
                ))}
                {
                    // flag && 
                    // <DropdownMenuItem>
                    //     <ShareUser
                    //         width={14}
                    //         height={16}
                    //         className="w-[14] h-4 object-contain fill-b4 me-2.5"
                    //     />
                    //     {'Share'}
                    // </DropdownMenuItem>
                }
            </DropdownMenuContent>
        </DropdownMenu>
    );
};

export default DropDownMenu;
