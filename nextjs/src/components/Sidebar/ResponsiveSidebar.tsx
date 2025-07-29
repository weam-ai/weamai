'use client';
import Humburger from '@/icons/HumburgerIcon';
import { ModelOptions } from '../Shared/ModelOptions';
import { memo } from 'react';
import Close from '@/icons/Close';
import { useSidebar } from '@/context/SidebarContext';

const ResponsiveSidebar = memo(({ children }) => {
    const { isOpen, toggleSidebar, closeSidebar } = useSidebar();
    
    return  (        
        <>
            <div className='absolute max-lg:fixed top-[30px] left-[15px] z-[15]' onClick={toggleSidebar}>
                <Humburger
                    width={22}
                    height={10}
                    className='fill-b2 w-[20px] h-auto mr-3 cursor-pointer'
                />
            </div>
            
            {/* Overlay when sidebar is open on mobile */}
            {isOpen && (
                <div 
                    className="fixed inset-0 bg-black/50 z-[30]" 
                    onClick={closeSidebar}
                />
            )}
            
            <div className={`sidebar flex h-full fixed z-[40] top-0 bottom-0 left-0 bg-white w-[290px] transition-all duration-300 ${!isOpen ? 'max-lg:left-[-100%]' : 'max-lg:left-0'}`}>
                {isOpen && (
                    <button 
                        className="fixed top-4 right-4 z-[40] lg:hidden transition-all duration-300" 
                        onClick={closeSidebar}
                    >
                        <Close
                            width={20}
                            height={20}
                            className="fill-white"
                        />
                    </button>                
                )}
                {children}
            </div>
        </>
    )
});
export default ResponsiveSidebar;