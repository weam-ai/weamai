import {
    BillingIcon,
    DataControlIcon,
    MembersIcon,
    SettingsIcon,
} from '@/icons/SettingsIcon';
import Link from 'next/link';
import React from 'react';
import { LINK } from '@/config/config';
import { getSessionUser } from '@/utils/handleAuth';
import { ROLE_TYPE } from '@/utils/constant';
import UserProfile from './UserProfile';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
import routes from '@/utils/routes';
import Setting from '@/icons/Setting';
import TemplateIcon from '@/icons/TemplateIcon';
import Notification from './Notification';
import NotificationDot from './NotificationDot';
import SupportIcon from '@/icons/SupportIcon';
import ArrowBack from '@/icons/ArrowBack';
import StorageIcon from '@/icons/StorageIcon';
import { SettingActiveIcon, TemplateLibrary } from './SettingSelection';
import ReportIcon from '@/icons/ReportIcon';
import PrivateVisible from '../Brains/PrivateVisible';
import dynamic from 'next/dynamic';
import AppIcon from '@/icons/AppsIcon';
import CreditControlIcon from '@/icons/CreditControlIcon';

const BackButton = dynamic(() => import('./BackButton'), { ssr: false });
const SettingsLink = dynamic(() => import('./SettingsLink'), { ssr: false });

const SettingSidebar = async () => {
    const userDetail = await getSessionUser();
    
    const settingOptions = [
        {
            name: 'Reports',
            icon: (
                <ReportIcon
                    height={20}
                    width={20}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: true,
            navigate: `${LINK.DOMAIN_URL}/settings/reports`,
            slug: '/settings/reports',
        },
        {
            name: 'Connections',
            icon: (
                <AppIcon
                    height={20}
                    width={20}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: true,
            navigate: `${LINK.DOMAIN_URL}/mcp`,
            slug: '/mcp',
        },
        {
            name: 'General',
            icon: (
                <SettingsIcon
                    height={20}
                    width={20}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: true,
            navigate: `${LINK.DOMAIN_URL}/settings/general`,
            slug: '/settings/general',
        },
        {
            name: 'Data Controls',
            icon: (
                <DataControlIcon
                    height={20}
                    width={20}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: true,
            navigate: `${LINK.DOMAIN_URL}/settings/data-controls`,
            slug: '/settings/data-controls',
        },
        {
            name: 'Configuration',
            icon: (
                <DataControlIcon
                    height={20}
                    width={20}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: (userDetail?.roleCode == ROLE_TYPE.USER) ? false : true,
            navigate: `${LINK.DOMAIN_URL}/settings/config`,
            slug: '/settings/config',
        },
        {
            name: 'Members',
            icon: (
                <MembersIcon
                    height={20}
                    width={20}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: (userDetail?.roleCode == ROLE_TYPE.USER) ? false : true,
            navigate: `${LINK.DOMAIN_URL}/settings/members`,
            slug: '/settings/members',
        },
        {
            name: 'Storage',
            icon: (
                <StorageIcon
                    height={20}
                    width={20}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: userDetail?.roleCode == ROLE_TYPE.COMPANY,
            navigate: `${LINK.DOMAIN_URL}/settings/billing`,
            slug: '/settings/billing',
        },
        {
            name: 'Support',
            icon: (
                <SupportIcon
                    height={18}
                    width={18}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: userDetail?.roleCode !== ROLE_TYPE.USER,
            navigate: 'https://weamai.freshdesk.com/support/tickets/new?ticket_form=report_an_issue',
            slug: '/support',
            target: '_blank',
        },
        {
            name: 'Credit Control',
            icon: (
                <CreditControlIcon
                    height={20}
                    width={20}
                    className={'w-[18px] h-auto object-contain fill-b2'}
                />
            ),
            hasAccess: (userDetail?.roleCode == ROLE_TYPE.COMPANY) ? true : false,
            navigate: `${LINK.DOMAIN_URL}/settings/credit-control`,
            slug: '/settings/credit-control',
        },
    ];
    return (
        <>
            <div className="flex items-center justify-between border-b border-b10">
                <BackButton />
                <div className="w-full py-4 pl-3 relative font-bold">
                    Settings
                </div>
            </div>
            
            <div className="sidebar-sub-menu-items flex flex-col flex-1 relative h-full overflow-hidden pb-8">
                <div className="h-full overflow-y-auto w-full px-2.5">
                    <div className="my-2.5">
                        {settingOptions.map((setting, index) => {
                            return (
                                setting.hasAccess && (
                                    <SettingActiveIcon
                                        key={index}
                                        setting={setting}
                                    >
                                        <div className="menu-item-icon mr-2.5">
                                            {setting.icon}
                                        </div>
                                        <div className="menu-item-label text-font-14 font-normal leading-[20px] text-b2">
                                            {setting.name}
                                        </div>
                                    </SettingActiveIcon>
                                )
                            );
                        })}
                    </div>
                </div>
            </div>

            <div className='flex items-center justify-between px-5 py-1 mt-auto border-t bg-b12'>
                <div className='relative inline-block hover:bg-b5 hover:bg-opacity-[0.2] w-10 h-10 rounded-full text-center'>
                    <UserProfile />
                </div>
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <SettingsLink />
                        </TooltipTrigger>
                        <TooltipContent side="top" className="border-none">
                        <p className='text-font-14'>Settings</p>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <TemplateLibrary />
                        </TooltipTrigger>
                        <TooltipContent side="top" className="border-none">
                            <p className='text-font-14'>Agents and Prompts library</p>
                        </TooltipContent>
                    </Tooltip>
                </TooltipProvider>
                <div className='relative inline-block'>
                    <div className="hidden">
                        {/* <SSESubscription /> */}
                        <PrivateVisible/>
                    </div>
                    <Notification />
                    <NotificationDot />
                </div>
                            
                            
            </div>
        </>
    );
};

export default SettingSidebar;



