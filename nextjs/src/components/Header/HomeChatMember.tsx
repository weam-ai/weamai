'use client'
import { getCurrentUser } from '@/utils/handleAuth';
import React, { useMemo } from 'react'
import ProfileImage from '../Profile/ProfileImage';

const HomeChatMember = () => {
    const currentUser = useMemo(() => getCurrentUser(), []);
    return (
        <div
            className="avatar-group md:p-[5px] p-0.5 bg-b15 rounded-[100px] border border-b11 cursor-pointer"
        >
            <div className="flex -space-x-1 overflow-hidden">
                <ProfileImage
                    key={currentUser?._id}
                    user={currentUser}
                    w={30}
                    h={30}
                    classname={'rounded-full object-cover h-8'}
                    spanclass={'user-char flex items-center justify-center size-8 rounded-full bg-[#B3261E] text-b15 text-font-16 font-normal mr-0'}
                />
            </div>
        </div>
    );
}

export default HomeChatMember