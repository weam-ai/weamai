import React, { useMemo } from 'react';
import { LINK } from '@/config/config';
import { usePathname, useRouter } from 'next/navigation';
import UserSetting from '@/icons/UserSetting';
import SecureIcon from '@/icons/SecureIcon';
import LockIcon from '@/icons/Lock';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
import TemplateIcon from '@/icons/TemplateIcon';
import Notification from './Notification';
import NotificationDot from './NotificationDot';
import UserProfile from './UserProfile';
import ArrowBack from '@/icons/ArrowBack';
import { GENERAL_BRAIN_TITLE } from '@/utils/constant';
import { getCurrentUser } from '@/utils/handleAuth';
import { encodedObjectId, generateObjectId } from '@/utils/helper';
import { RootState } from '@/lib/store';
import { useSelector } from 'react-redux';
import { BrainListType } from '@/types/brain';
import Link from 'next/link';
import { useSidebar } from '@/context/SidebarContext';
import BackButton from './BackButton';
import SettingsLink from './SettingsLink';
import { TemplateLibrary } from './SettingSelection';

const ProfileSidebar = () => {
    const pathname = usePathname();
    const router = useRouter();
    const objectId = useMemo(() => generateObjectId(), []);
    const brainData = useSelector((store: RootState) => store.brain.combined);
    const { closeSidebar } = useSidebar();

    const settingOptions = [
        {
            name: 'General',
            icon: (
                <UserSetting
                    height={20}
                    width={20}
                    className={'w-5 h-5 object-contain fill-b2'}
                />
            ),
            hasAccess: true,
            navigate: `${LINK.DOMAIN_URL}/profile-setting`,
            slug: '/profile-setting',
        },
        {
            name: 'Password',
            icon: (
                <LockIcon 
                height={20}
                    width={20}
                    className={'w-5 h-5 object-contain fill-b2'}
                />
            ),
            hasAccess: true,
            navigate: `${LINK.DOMAIN_URL}/profile-setting/password`,
            slug: '/profile-setting/password',
        },
        {
            name: 'Two-Factor Authentication',
            icon: (
                <SecureIcon
                    height={20}
                    width={20}
                    className={'w-5 h-5 object-contain fill-b2'}
                />
            ),
            hasAccess: true,
            navigate: `${LINK.DOMAIN_URL}/profile-setting/two-factor-authentication`,
            slug: '/profile-setting/two-factor-authentication',
        },
        
    ];
    // Function to handle navigation link clicks
    const handleLinkClick = () => {
        closeSidebar();
    };
    return (
        <>
            
            <div className="flex items-center justify-between border-b border-b10">
                <BackButton />
                <div className="w-full py-4 pl-3 relative font-bold">
                    Profile Settings
                </div>
            </div>

            <div className="sidebar-sub-menu-items flex flex-col relative h-full overflow-hidden pb-8">
                <div className="h-full overflow-y-auto w-full px-2.5">
                    <div className="my-2.5">
                        {settingOptions.map((setting, index) => {
                            return (
                                setting.hasAccess && (
                                    <Link
                                        key={index}
                                        href={setting.navigate}
                                        className={`${
                                            pathname === setting.slug
                                                ? 'active'
                                                : ''
                                        } sidebar-sub-menu-items cursor-pointer flex items-center py-2.5 px-5 mb-2 rounded-custom hover:bg-b11 [&.active]:bg-b12`}
                                        onClick={closeSidebar}
                                    >
                                        <div className="menu-item-icon mr-2.5">
                                            {setting.icon}
                                        </div>
                                        <div className="menu-item-label text-font-15 font-normal leading-[20px] text-b2">
                                            {setting.name}
                                        </div>
                                    </Link>
                                )
                            );
                        })}
                    </div>
                </div>
            </div>
            <div className='flex items-center justify-between px-5 py-1 mt-auto border-t bg-b12'>
                <div className='relative inline-block bg-b5 bg-opacity-[0.2] w-10 h-10 rounded-full text-center'>
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
                    <Notification />
                    <NotificationDot />
                </div>
                            
                            
            </div>
        </>
    );
};

export default ProfileSidebar;
