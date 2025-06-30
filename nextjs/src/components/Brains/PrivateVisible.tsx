'use client';

import useUsers from '@/hooks/users/useUsers';
import { getCurrentUser } from '@/utils/handleAuth';
import { useMemo, memo, useEffect } from 'react';

export type PrivateVisibleProps = {
    children?: React.ReactNode;
};

const PrivateVisible = memo<PrivateVisibleProps>(({ children }) => {
    const currentUser = useMemo(() => getCurrentUser(), []);
    const { getUserById } = useUsers();


    useEffect(() => {
        getUserById(currentUser?._id);
    }, []);

    if (currentUser?.isPrivateBrainVisible) {
        return children;
    }

    return null;
});

export default PrivateVisible;
