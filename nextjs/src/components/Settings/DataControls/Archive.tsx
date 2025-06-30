import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import ArchiveBrain from './ArchiveBrain';
import { getSessionUser } from '@/utils/handleAuth';
import { hasPermission, PERMISSIONS, Role } from '@/utils/permission';
import routes from '@/utils/routes';
import Link from 'next/link';
import { Suspense } from 'react';
import { DataControls, StorageLoader } from '@/components/Loader/DataControls';
import dynamic from 'next/dynamic';
const ArchiveWorkspace = dynamic(() => import('./ArchiveWorkspace'), { ssr: true, loading: () => <DataControls items={10} /> });
const Storage = dynamic(() => import('./Storage'), { ssr: true, loading: () => <StorageLoader /> });

const WORKSPACE_TAB = 'workspace';
const STORAGE_TAB = 'storage';
const BRAIN_TAB = 'brain';
const Archive = async ({ tab }) => {
    const sessionUser = await getSessionUser();

    return (
        <Tabs
            defaultValue='Brain'
            className="w-full mx-auto mt-0 lg:mt-4"
        >
            <TabsList className="flex p-0 space-x-6">
                    <Link href={`${routes.dataControls}?tab=${BRAIN_TAB}`}>
                        <TabsTrigger value="Brain" className="px-0 max-md:text-font-12">
                                Archived Brains
                        </TabsTrigger>
                    </Link>
                {hasPermission(sessionUser?.roleCode as Role , PERMISSIONS.ARCHIVE_WORKSPACE) &&
                        <Link href={`${routes.dataControls}?tab=${WORKSPACE_TAB}`}>
                            <TabsTrigger value="Workspace" className="px-0 max-md:text-font-12">
                                    Archived Workspaces
                            </TabsTrigger>
                        </Link>
                }
                    <Link href={`${routes.dataControls}?tab=${STORAGE_TAB}`}>
                        <TabsTrigger value="Storage" className="px-0 max-md:text-font-12">
                                Storage
                        </TabsTrigger>
                    </Link>
            </TabsList>
            <TabsContent
                value="Brain"
                className="py-5 px-0"
            >
                <ArchiveBrain />
            </TabsContent>
            {hasPermission(sessionUser?.roleCode as Role, PERMISSIONS.ARCHIVE_WORKSPACE) &&
                <TabsContent
                    value="Workspace"
                    className="py-5 px-0"
                >
                    {tab === WORKSPACE_TAB && (<Suspense fallback={<DataControls items={10}/>}>
                        <ArchiveWorkspace />
                    </Suspense>)}
                </TabsContent>
            }
            <TabsContent
                value="Storage"
                className="p-5 pt-0"
            >
                {tab === STORAGE_TAB && (<Suspense fallback={<StorageLoader/>}>
                    <Storage />
                </Suspense>)}
            </TabsContent>
        </Tabs>
    );
}

export default Archive;


// 'use client';
// import React, { useEffect, useState } from 'react';
// import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
// import useModal from '@/hooks/common/useModal';
// import ArchiveBrain from './ArchiveBrain';
// import ArchiveWorkspace from './ArchiveWorkspace';
// import useBrains from '@/hooks/brains/useBrains';
// import { useSelector } from 'react-redux';
// import useWorkspaceList from '@/hooks/workspace/useWorkspaceList';
// import { getCurrentUser } from '@/utils/handleAuth';
// import { ROLE_TYPE } from '@/utils/constant';
// import DoughnutChartStorage from '@/components/Settings/DoughnutChartStorage';
// import { bytesToMegabytes } from '@/utils/common';
// import RequestMoreStorageModal from '@/components/Settings/RequestMoreStorageModal';
// import useStorage from '@/hooks/storage/useStorage';
// import { RootState } from '@/lib/store';

// const Archive = () => {

//     const { isOpen, openModal, closeModal } = useModal();

//     const { getArchiveBrainList, privateLoading } = useBrains({
//         isShare: false,
//         addMember: false,
//     });
//     const [selectedTab, setSelectedTab] = useState('Brain');
//     const { getArchiveWorkspace } = useWorkspaceList();

//     const userDetail = getCurrentUser();

//     useEffect(() => {
//         if (selectedTab == 'Workspace') {
//             getArchiveWorkspace();
//         } else {
//             getArchiveBrainList();
//         }
//     }, [selectedTab]);

//     const archiveBrainList = useSelector((store: RootState) => store.brain.archiveBrains);
//     const archiveWorkspace = useSelector((store: RootState) => store.workspacelist.archivelist);

//     const {
//         isOpen: requestMoreStorage,
//         openModal: requestMoreStorageOpen,
//         closeModal: closeRequestMoreStorage,
//     } = useModal();

//     const { getStorage, storageDetails, updateStorage } = useStorage();

//     useEffect(() => {
//         getStorage();
//     }, []);

//     return (
//         <Tabs
//             defaultValue="Brain"
//             className="w-full lg:px-5 px-3 mx-auto mt-0 lg:mt-4"
//             onValueChange={(newValue) => { setSelectedTab(newValue) }}
//         >
//             <TabsList className="flex p-0">
//                 <TabsTrigger value="Brain" className="px-4">
//                     Archive Brain
//                 </TabsTrigger>
//                 {(userDetail?.roleCode != ROLE_TYPE.USER) &&
//                     <TabsTrigger value="Workspace" className="px-4">
//                         Archive Workspace
//                     </TabsTrigger>
//                 }
//                 <TabsTrigger value="Storage" className="px-4">
//                     Storage
//                 </TabsTrigger>
//             </TabsList>
//             <TabsContent
//                 value="Brain"
//                 className="py-5 px-0"
//             >
//                 <ArchiveBrain archiveBrainList={archiveBrainList} />
//             </TabsContent>
//             {(userDetail?.roleCode != ROLE_TYPE.USER) &&
//                 <TabsContent
//                     value="Workspace"
//                     className="py-5 px-0"
//                 >
//                     <ArchiveWorkspace archiveWorkspace={archiveWorkspace} />
//                 </TabsContent>
//             }
//             <TabsContent
//                 value="Storage"
//                 className="p-5 pt-0"
//             >
//                 <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
//                     <div className="border border-b11 rounded-custom p-5">
//                         <div className="relative flex items-center justify-center">
//                             <DoughnutChartStorage
//                                 used={bytesToMegabytes(storageDetails?.used)}
//                                 total={bytesToMegabytes(storageDetails?.total)}
//                             />
//                         </div>
//                     </div>
//                     <div className="flex flex-col justify-center items-center">
//                         <p className="mb-2.5 text-font-16 font-normal text-b2">
//                             Need more storage?
//                         </p>
//                         <button
//                             className="btn btn-blue"
//                             onClick={() =>
//                                 requestMoreStorageOpen()
//                             }
//                         >
//                             Request For More Storage
//                         </button>
//                         {requestMoreStorage && (
//                             <RequestMoreStorageModal
//                                 open={
//                                     requestMoreStorageOpen
//                                 }
//                                 closeModal={
//                                     closeRequestMoreStorage
//                                 }
//                                 updateStorage={
//                                     updateStorage
//                                 }
//                             />
//                         )}
//                     </div>
//                     {/* <AssignUsers
//                         name={'Workspaces'}
//                         count={'25'}
//                         icon={
//                             <WorkSpaceIcon
//                                 width={24}
//                                 height={24}
//                                 className="w-6 h-6 fill-b2 me-3"
//                             />
//                         }
//                     /> */}

//                     {/* <AssignUsers
//                         name={'Brains'}
//                         count={'05'}
//                         isBrain={true}
//                         icon={
//                             <BrainIcon
//                                 width={24}
//                                 height={24}
//                                 className="w-6 h-6 fill-b2 me-3"
//                             />
//                         }
//                     /> */}
//                 </div>
//             </TabsContent>
//         </Tabs>
//     );
// }

// export default Archive;


