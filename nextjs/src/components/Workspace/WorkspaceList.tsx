import DownArrowIcon from '@/icons/DownArrow';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import Mainlogo from '@/icons/Mainlogo';
import Link from 'next/link';
import { EditWorkspaceIcon, WorkspaceAddButton, WorkspaceSelection } from './DropDownOptions';
import { WorkspaceListType } from '@/types/workspace';
import GlobalSearch from '../Search/GlobalSearch';
import dynamic from 'next/dynamic';
import { SelectedWorkspaceProps } from './SelectedWorkspace';
import { BrainListType } from '@/types/brain';
const SelectedWorkspace = dynamic<SelectedWorkspaceProps>(() => import('./SelectedWorkspace').then(mod => mod.default), { ssr: false });

type WorkspaceDropdownProps = {
    workspaceList: WorkspaceListType[];
    session: any;
    brainList: BrainListType[];
};

const WorkspaceDropdown = async ({ workspaceList, session, brainList }: WorkspaceDropdownProps) => {
    const user = session?.user;
    return (
        <div className='flex items-center justify-between border-b border-b10'>
            <div className="logo w-9 h-9 ml-2 flex items-center justify-center rounded-md">
                <Link href={"#"}>
                    <Mainlogo width={'32'} height={'32'} className={"fill-white"} />
                </Link>
            </div>
            <div className="w-full py-4 pl-3 pr-6 relative">
                {workspaceList?.length > 0 && (
                    <DropdownMenu className="workspace-list-dropdown">
                        <DropdownMenuTrigger className="text-font-16 leading-[1.3] font-bold text-b2 flex w-full items-center transition duration-150 ease-in-out focus:outline-none focus:ring-0 motion-reduce:transition-none [&[data-state=open]>span>.drop-arrow]:rotate-180">
                            <SelectedWorkspace workspaceList={workspaceList} />
                            <span className="ml-auto">
                                <DownArrowIcon
                                    width={'14'}
                                    height={'8'}
                                    className="drop-arrow w-3.5 h-2 object-contain fill-b6 transition duration-150 ease-in-out"
                                />
                            </span>
                        </DropdownMenuTrigger>

                        <DropdownMenuContent
                            align="start"
                            className="md:min-w-[250px] !rounded-[15px]"
                        >
                            <div className="max-h-80 overflow-y-auto">
                            {workspaceList.map((w: WorkspaceListType) => (
                                <div key={w._id} className="group flex items-center cursor-pointer focus:outline-none hover:bg-b12">
                                    <WorkspaceSelection w={w} brainList={brainList} />
                                    <EditWorkspaceIcon w={w} user={user} />
                                </div>
                            ))}
                            </div>
                            <WorkspaceAddButton user={user} />
                        </DropdownMenuContent>
                    </DropdownMenu>
                )}
            </div>
            <GlobalSearch />
        </div>
    );
};

export default WorkspaceDropdown;