'use client';
import { setSelectedWorkSpaceAction } from "@/lib/slices/workspace/workspacelist";
import { RootState } from "@/lib/store";
import { WorkspaceListType } from "@/types/workspace";
import { truncateText } from "@/utils/common";
import { decryptedPersist, encryptedPersist } from "@/utils/helper";
import { WORKSPACE } from "@/utils/localstorage";
import { useDispatch, useSelector } from "react-redux";
import { memo } from "react";

export type SelectedWorkspaceProps = {
    workspaceList: WorkspaceListType[];
}
const SelectedWorkspace = memo<SelectedWorkspaceProps>(({ workspaceList }) => {
    const selectedWorkSpace = useSelector((store: RootState) => store.workspacelist.selected);
    const dispatch = useDispatch();
    return (
        <span className="truncate">
            {(() => {
                if (!selectedWorkSpace) {
                    const workspace = decryptedPersist(WORKSPACE)
                        ? decryptedPersist(WORKSPACE)
                        : workspaceList[0];
                    encryptedPersist(workspace, WORKSPACE);
                    dispatch(setSelectedWorkSpaceAction(workspace));
                    return workspace.title;
                } 
                const updatedWorkspace = workspaceList.find((workspace: WorkspaceListType) => workspace._id === selectedWorkSpace?._id);
                return truncateText(updatedWorkspace?.title, 15);
            })()}
        </span>
    );
});

export default SelectedWorkspace;