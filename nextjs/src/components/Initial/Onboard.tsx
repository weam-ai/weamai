'use client';
import React, { useMemo } from 'react';
import InviteForm from './InviteForm';
import { ROLE_TYPE } from '@/utils/constant';
import MagicInviteDetails from '../Auth/Register/MagicInviteDetails';
import { getCurrentUser } from '@/utils/handleAuth';
import { redirect } from 'next/navigation';
import routes from '@/utils/routes';
import { isUserNameComplete } from '@/utils/helper';
import { usePathname } from 'next/navigation';
const Onboard = () => {
    const currentUser = useMemo(() => getCurrentUser(), []);
    const currentPath = usePathname();

    const isCompanyUser = useMemo(
        () => currentUser?.roleCode === ROLE_TYPE.COMPANY,
        [currentUser]
    );

    const content = useMemo(() => {
        if (!isUserNameComplete(currentUser) && currentPath !== routes.onboard) {
            redirect(routes.onboard);
        } else if (isUserNameComplete(currentUser) && currentPath === routes.onboard && !isCompanyUser) {
            redirect(routes.main);
        }
        
        if (isCompanyUser) return <InviteForm />;
        return <MagicInviteDetails email={currentUser?.email} />;

    }, [isCompanyUser]);

    return <>{content}</>;
};

export default Onboard;
