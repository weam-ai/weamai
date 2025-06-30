'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React from 'react';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
const SideBarIconMenuList = ({ icons }) => {
    const pathname = usePathname();

    return (
        <>
            {icons.map((i) => {
                return (
                    <li key={i.id}>
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                <Link
                                    href={i.href}
                                    className={`${
                                        i.href == pathname ? 'active' : ''
                                    } group relative w-10 h-10 flex items-center justify-center rounded-full ease-in-out duration-150 bg-transparent hover:bg-white hover:bg-opacity-[0.2] [&.active]:bg-white [&.active]:bg-opacity-[0.1] `}
                                >
                                    {i?.isNotification && (
                                        <div className="absolute bottom-auto left-auto right-2.5 top-1.5 z-10 inline-block rounded-full bg-red w-1.5 h-1.5"></div>
                                    )}
                                    {i.value}
                                </Link>
                                </TooltipTrigger>
                                <TooltipContent side="left" className="border-none">
                                <p className='text-font-14'>{i.name}</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        
                    </li>
                );
            })}
        </>
    );
};

export default SideBarIconMenuList;
