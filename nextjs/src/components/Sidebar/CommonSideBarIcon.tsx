import Mainlogo from '@/icons/Mainlogo';
import Setting from '@/icons/Setting';
import UserProfile from './UserProfile';
import routes from '@/utils/routes';
import HomeIcon from '@/icons/HomeIcon';
import SideBarIconMenuList from './SideBarIconMenuList';
import Notification from './Notification';
import Link from 'next/link';
import TemplateIcon from '@/icons/TemplateIcon';
import SupportIcon from '@/icons/SupportIcon';
import NotificationDot from './NotificationDot';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
import SSESubscription from '../Subscription/SSESubscription';
const CommonSideBarIcon = () => {
    const icons = [
        {
            id: 1,
            value: (
                <HomeIcon
                    width={'20'}
                    height={'20'}
                    className="w-5 h-5 object-contain fill-white"
                />
            ),
            href: routes.main,
            name: 'Home',
        },
        {
            id: 2,
            value: (
                <TemplateIcon
                    width={'20'}
                    height={'20'}
                    className="w-5 h-5 object-contain fill-white"
                />
            ),
            href: routes.customTemplates,
            name: 'Agents and Prompts library',
        },
    ];
    return (
        <div className="sidebar-menu flex flex-col  bg-blue py-5 px-2 md:px-4 h-full">
            <div className="logo w-10 h-10 flex items-center justify-center rounded-full shadow-[0_0_10px_rgba(0,0,0,0.4)]">
                <Mainlogo width={'40'} height={'40'} />
            </div>
            <div className="sidebar-menu-items mt-5">
                <ul className="p-0 mt-[15px] mx-0 mb-0 flex flex-col gap-[15px]">
                    <SideBarIconMenuList icons={icons} />
                    <li className="group relative">
                        {/* <div className="hidden">
                            <SSESubscription />
                        </div> */}
                        <Notification />
                        <NotificationDot />
                    </li>
                </ul>
            </div>
            <div className="sidebar-menu-items mt-auto">
                <ul className="p-0 mt-[15px] mx-0 mb-0 flex flex-col gap-[10px]">
                <li>
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                            <Link
                                href={"https://weamai.freshdesk.com/support/tickets/new?ticket_form=report_an_issue"}
                                target='_blank'
                                className="group relative w-10 h-10 flex items-center justify-center rounded-full ease-in-out duration-150 bg-transparent hover:bg-white hover:bg-opacity-[0.2] [&.active]:bg-b10"
                                >
                                <SupportIcon className={"fill-white w-4 h-4"} />
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="left" className="border-none">
                            <p className='text-font-14'>Support</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                    </li>
                    <li>
                    <TooltipProvider>
                        <Tooltip>
                            <TooltipTrigger asChild>
                                <Link
                                href={routes.setting}
                                className="group relative w-10 h-10 flex items-center justify-center rounded-full ease-in-out duration-150 bg-transparent hover:bg-white hover:bg-opacity-[0.2] [&.active]:bg-b10"
                                >
                                <Setting className={"fill-white w-4 h-4"} />
                                </Link>
                            </TooltipTrigger>
                            <TooltipContent side="left" className="border-none">
                            <p className='text-font-14'>Settings</p>
                            </TooltipContent>
                        </Tooltip>
                    </TooltipProvider>
                    </li>
                    
                </ul>
            </div>

            <UserProfile />
        </div>
    );
};

export default CommonSideBarIcon;
