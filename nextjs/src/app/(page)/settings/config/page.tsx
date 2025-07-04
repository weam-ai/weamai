import React, { Suspense } from 'react';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
// import Environment from '@/components/Settings/Configuration/Environment';
// import ProAgents from '@/components/Settings/Configuration/ProAgents';
import APIKeyConfig from '@/components/Settings/Configuration/APIKeyConfig';
import Link from 'next/link';
import routes from '@/utils/routes';
import APIKeyConfigLoader from '@/components/Loader/APIKeyConfigLoader';

const TABS = {
    //environment: 'environment',
    apiKey: 'apiKey',
    //proAgents: 'proAgents',
} as const;

export default function Configuration() {
    const tab = 'apiKey';
    //const renderTab = TABS[tab as keyof typeof TABS];
    return (
        <div className="flex flex-col flex-1 relative h-full overflow-hidden lg:pt-20 pb-10 px-2 max-md:mt-[50px]">
            <div className="h-full overflow-y-auto w-full relative">
                <div className="mx-auto max-w-[950px]">
                    <Tabs
                        defaultValue="apiKey"
                        className="w-full mx-auto mt-0 lg:mt-4"
                    >
                        <TabsList className="flex p-0 space-x-6">
                            {/* <Link href={`${routes.Settingconfig}?tab=environment`}>
                                <TabsTrigger value="environment" className="px-0">
                                    Environment
                                </TabsTrigger>
                            </Link> */}
                            <Link href={`${routes.Settingconfig}?tab=apiKey`}>
                                <TabsTrigger value="apiKey" className="px-0">
                                    API Key
                                </TabsTrigger>
                            </Link>
                            {/* <Link href={`${routes.Settingconfig}?tab=proAgents`}>
                                <TabsTrigger value="proAgents" className="px-0">
                                    Pro Agents
                                </TabsTrigger>
                            </Link> */}
                        </TabsList>

                        {/* <TabsContent value="environment">
                            <Environment />
                        </TabsContent> */}

                        <TabsContent value="apiKey">
                            {
                                //renderTab === TABS.apiKey && (
                                    <Suspense fallback={<APIKeyConfigLoader count={3} />}>
                                        <APIKeyConfig tab={tab} />
                                    </Suspense>
                                //)
                            }
                        </TabsContent>

                        {/* <TabsContent value="proAgents">
                            {
                                renderTab === TABS.proAgents && (
                                    <Suspense fallback={<div>Loading...</div>}>
                                        <ProAgents tab={tab}/>
                                    </Suspense>
                                )
                            }
                        </TabsContent> */}
                    </Tabs>
                </div>
            </div>
        </div>
    );
}
