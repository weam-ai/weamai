import Archive from '@/components/Settings/DataControls/Archive';

export default function DataControlsSettings({ searchParams }) {
    const tab = searchParams.tab;
    return (
        <>
            <div className="flex flex-col flex-1 relative h-full overflow-hidden lg:pt-20 pb-10 px-2 max-md:mt-[50px]">
                <div className="h-full overflow-y-auto w-full relative">
                    <div className="mx-auto md:max-w-[950px] max-w-full">
                        <Archive tab={tab}/>
                    </div>
                </div>
            </div>
        </>
    );
}

// 'use client';
// import React, { useEffect } from 'react';
// import Archive from '@/components/Settings/DataControls/Archive';

// export default function DataControlsSettings() {
//     return (
//         <>
//             <div className="flex flex-col flex-1 relative h-full overflow-hidden lg:pt-20 pb-10 px-2">
//                 <div className="h-full overflow-y-auto w-full relative">
//                     <div className="mx-auto max-w-[730px]">
//                         <Archive />
//                     </div>
//                 </div>
//             </div>
//         </>
//     );
// }