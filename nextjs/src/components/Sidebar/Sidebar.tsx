import SidebarPages from './SidebarPages';
import ResponsiveSidebar from './ResponsiveSidebar';
import MainPageSidebar from './MainPageSidebar';
import { Suspense } from 'react';
import SettingSidebar from './SettingSidebar';
const Sidebar = () => {
    return (
        <ResponsiveSidebar>
            <SidebarPages responsewidth={'w-[290px]'} settingSidebar={<SettingSidebar/>}>
                {/* <Suspense fallback={<Spinner/>}> */}
                    <MainPageSidebar/>
                {/* </Suspense> */}
            </SidebarPages>
        </ResponsiveSidebar>
    )
};
export default Sidebar;


