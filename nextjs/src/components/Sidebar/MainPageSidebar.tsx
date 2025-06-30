import AddBrainButton from '../Brains/AddBrainButton';
import WorkspaceDropdown from '../Workspace/WorkspaceList';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from '../ui/tooltip';
import Link from 'next/link';
import Notification from './Notification';
import NotificationDot from './NotificationDot';
import UserProfile from './UserProfile';
import SSESubscription from '../Subscription/SSESubscription';
import { getSession } from '@/config/withSession';
import { hasPermission, PERMISSIONS } from '@/utils/permission';
import { fetchWorkspaceList } from '@/actions/workspace';
import { fetchBrainList } from '@/actions/brains';
import { TemplateLibrary } from './SettingSelection';
import { PrivateVisibleProps } from '../Brains/PrivateVisible';
import { RESPONSE_STATUS, RESPONSE_STATUS_CODE } from '@/utils/constant';
import RefreshTokenClient from '../Shared/RefreshTokenClient';
import { WorkspaceNewChatButton } from '../Workspace/DropDownOptions';
import dynamic from 'next/dynamic';

const SettingsLink = dynamic(() => import('./SettingsLink'), { ssr: false });
const ShareBrainList = dynamic(() => import('../Brains/ShareBrainList'), { ssr: false });
const PrivateBrainList = dynamic(() => import('../Brains/PrivateBrainList'), { ssr: false });
const PrivateVisible = dynamic<PrivateVisibleProps>(() => import('../Brains/PrivateVisible').then(mod => mod.default), { ssr: false });

const MainPageSidebar = async () => {
    const [workspaceResponse, brainResponse, session] = await Promise.all([
        fetchWorkspaceList(),
        fetchBrainList(),
        getSession(),
    ]);
    // if (!brainList || !workspaceList) return null;
    const user = session?.user;
    const workspaceList = workspaceResponse?.data;
    const brainList = brainResponse?.data;

    return (
        <>
            {(workspaceResponse?.status === RESPONSE_STATUS.UNAUTHORIZED ||
                brainResponse?.status === RESPONSE_STATUS.UNAUTHORIZED) &&
                (workspaceResponse?.code ===
                    RESPONSE_STATUS_CODE.REFRESH_TOKEN ||
                    brainResponse?.code ===
                        RESPONSE_STATUS_CODE.REFRESH_TOKEN) && (
                    <RefreshTokenClient />
                )}
            <WorkspaceDropdown
                workspaceList={workspaceList}
                session={session}
                brainList={brainList}
            />

            {workspaceList?.length > 0 && (
                <div className="sidebar-sub-menu-items flex flex-col h-full overflow-hidden">
                    <div className="h-full w-full flex flex-col px-3 overflow-y-auto pb-3 pt-4">
                        <WorkspaceNewChatButton />
                        <div className="flex w-full justify-between pr-1 group mb-4">
                            <h2 className="font-bold text-font-14">
                                SHARED BRAINS
                            </h2>
                            <AddBrainButton
                                text={'Add a Shared Brain'}
                                isPrivate={false}
                            />
                        </div>
                        <ShareBrainList brainList={brainList} workspaceFirst={workspaceList[0]} />
                        <PrivateVisible>
                            <div className="flex w-full border-t border-b10 mt-5 pt-5 pr-1 justify-between group mb-4">
                                <h2 className="font-bold text-font-14">
                                    PRIVATE BRAINS
                                </h2>
                                <AddBrainButton
                                    text={'Add a Private Brain'}
                                    isPrivate={true}
                                />
                            </div>
                            <PrivateBrainList brainList={brainList} workspaceFirst={workspaceList[0]} />
                        </PrivateVisible>
                        {hasPermission(
                        user?.roleCode,
                        PERMISSIONS.UPGRADE_PLAN
                        ) && (
                        <Link
                            className="btn btn-outline-blue mt-auto"
                            href={'/settings/subscription'}
                        >
                            Upgrade Plan
                        </Link>
                        )}
                    </div>

                    <div className="flex items-center justify-between px-5 py-1 mt-auto border-t bg-b12">
                        <div className="relative inline-block hover:bg-b5 hover:bg-opacity-[0.2] w-10 h-10 rounded-full text-center">
                            <UserProfile />
                        </div>
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger asChild>
                                    <SettingsLink />
                                </TooltipTrigger>
                                <TooltipContent
                                    side="top"
                                    className="border-none"
                                >
                                    <p className="text-font-14">Settings</p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        <TooltipProvider>
                            <Tooltip>
                                <TooltipTrigger>
                                    <TemplateLibrary />
                                </TooltipTrigger>
                                <TooltipContent
                                    side="top"
                                    className="border-none"
                                >
                                    <p className="text-font-14">
                                        Agents and Prompts library
                                    </p>
                                </TooltipContent>
                            </Tooltip>
                        </TooltipProvider>
                        <div className="relative inline-block">
                            {/* <div className="hidden">
                                        <SSESubscription />
                                    </div> */}
                            <Notification />
                            <NotificationDot />
                        </div>
                    </div>
                </div>
            )}

            <div className="hidden">
                <PrivateVisible />
            </div>
        </>
    );
};

export default MainPageSidebar;
