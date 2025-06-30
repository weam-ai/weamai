'use client';
import { cacheShareList } from '@/lib/slices/brain/brainlist';
import { setSelectedWorkSpaceAction } from '@/lib/slices/workspace/workspacelist';
import { RootState } from '@/lib/store';
import { getCurrentUser } from '@/utils/handleAuth';
import { decryptedPersist } from '@/utils/helper';
import { WORKSPACE } from '@/utils/localstorage';
import { useDispatch, useSelector } from 'react-redux';
import { Accordion } from '../ui/accordion';
import { CommonList } from './BrainList';
import { useMemo } from 'react';
import { AllBrainListType } from '@/types/brain';
import { WorkspaceListType } from '@/types/workspace';

type ShareBrainListProps = {
    brainList: AllBrainListType[];
    workspaceFirst?: WorkspaceListType;
}

const ShareBrainList = ({ brainList, workspaceFirst }: ShareBrainListProps) => {
    const dispatch = useDispatch();
    const selectedWorkSpace = useSelector(
        (store: RootState) => store.workspacelist.selected
    );
    const currentUser = useMemo(() => getCurrentUser(), []);

    if (!selectedWorkSpace || !selectedWorkSpace._id) {
        const persistWorkspace = decryptedPersist(WORKSPACE);
        const setData = persistWorkspace ? persistWorkspace : workspaceFirst;
        dispatch(setSelectedWorkSpaceAction(setData));
    }

    const selectedWorkSpaceBrainList = brainList.find(
        (brain) => brain._id.toString() === selectedWorkSpace._id.toString()
    );

    const shareBrainList = selectedWorkSpaceBrainList?.brains.filter(
        (brain) => brain.isShare
    );

    const dispatchPayload = shareBrainList ? shareBrainList : [];

    dispatch(cacheShareList(dispatchPayload));
    return (
        <>
            {shareBrainList?.length > 0 && (
                <Accordion
                    type="single"
                    collapsible
                    className="w-full flex flex-col"
                >
                    {shareBrainList.map((b) => (
                        <CommonList
                            b={b}
                            key={b._id}
                            currentUser={currentUser}
                        />
                    ))}
                </Accordion>
            )}
        </>
    );
};

export default ShareBrainList;
