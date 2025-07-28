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
import { getSession } from '@/config/withSession';
import { fetchWorkspaceList } from '@/actions/workspace';
import { fetchBrainList } from '@/actions/brains';
import { TemplateLibrary } from './SettingSelection';
import { PrivateVisibleProps } from '../Brains/PrivateVisible';
import { WorkspaceNewChatButton } from '../Workspace/DropDownOptions';
import dynamic from 'next/dynamic'; 
import AddBrainButton from '../Brains/AddBrainButton';
import AppIcon from '@/icons/AppsIcon';

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
            {/* {(workspaceResponse?.status === RESPONSE_STATUS.FORBIDDEN ||
                brainResponse?.status === RESPONSE_STATUS.FORBIDDEN) &&
                (workspaceResponse?.code ===
                    RESPONSE_STATUS_CODE.REFRESH_TOKEN ||
                    brainResponse?.code ===
                        RESPONSE_STATUS_CODE.REFRESH_TOKEN) && (
                    <RefreshTokenClient />
                )} */}
            <WorkspaceDropdown
                workspaceList={workspaceList}
                session={session}
                brainList={brainList}
            />

            {workspaceList?.length > 0 && (
                <div className="sidebar-sub-menu-items flex flex-col h-full overflow-hidden">
                    <div className="h-full w-full flex flex-col px-3 overflow-y-auto pb-3 pt-4">
                        <WorkspaceNewChatButton />
                        <div className="w-full">
                            <Link
                            href="/mcp"
                            className="flex gap-x-3 text-font-14 items-center mb-5 cursor-pointer"
                        >
                            <AppIcon width={16} height={16} className={"size-4 fill-b6"} />
                            Connected Apps
                        </Link>
                        <div className="flex w-full justify-between pr-1 group mb-1 font-bold text-font-14">
                                <div className="flex justify-between w-full">
                                    <span className="pl-2">
                                        SHARED BRAINS
                                    </span>
                                </div>
                                <AddBrainButton text="Add Shared Brain" isPrivate={false} />
                            </div>
                            <div className="w-full flex flex-col mb-4 px-3 text-b6">
                                <ShareBrainList
                                    brainList={brainList}
                                    workspaceFirst={workspaceList[0]}
                                />
                            </div>
                        </div>
                        <PrivateVisible>
                            <div className="w-full border-t mt-5 pt-5">
                                <div className="flex w-full pr-1 justify-between group mb-4 font-bold text-font-14">
                                    <div className="flex justify-between w-full">
                                        <span className="pl-2">
                                            PRIVATE BRAINS
                                        </span>
                                    </div>
                                    <AddBrainButton text="Add Private Brain" isPrivate={true} />
                                </div>
                                <div className="w-full flex flex-col mb-4 px-3 text-b6">
                                    <PrivateBrainList
                                        brainList={brainList}
                                        workspaceFirst={workspaceList[0]}
                                    />
                                </div>
                            </div>
                        </PrivateVisible>
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
