import commonApi from '@/api';
import { setSelectedWorkSpaceAction, setWorkSpaceListAction, setArchiveWorkSpace } from '@/lib/slices/workspace/workspacelist';
import { MODULES, MODULE_ACTIONS } from '@/utils/constant';
import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Toast from '@/utils/toast';
import { removeObjectFromArray } from '@/utils/common';
import { decryptedPersist } from '@/utils/helper';
import { WORKSPACE } from '@/utils/localstorage';

const useWorkspaceList = () => {
    const [loading, setLoading] = useState(false);
    const dispatch = useDispatch();
    const workspaceList = useSelector((store:any) => store.workspacelist.list);
    const archiveWorkspace = useSelector((store:any) => store.workspacelist.archivelist);

    const getList = async () => {
        try {
            setLoading(true);
            if(workspaceList.length) return workspaceList
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.WORKSPACE,
                common: true,
                data: {
                    options: {
                        pagination: false
                    },
                    query:{
                        deletedAt: {
                            $exists: false
                        }
                    }
                },
            });
            dispatch(setWorkSpaceListAction(response.data))
            const persistWorkspace = decryptedPersist(WORKSPACE);
            const setData = persistWorkspace ? persistWorkspace : response.data[0];
            dispatch(setSelectedWorkSpaceAction(setData));
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    const getArchiveWorkspace = async () => {
        try {
            setLoading(true);
            const response = await commonApi({
                action: MODULE_ACTIONS.LIST,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.WORKSPACE,
                common: true,
                data: {
                    options: {
                        pagination: false
                    },
                    query: { 
                        deletedAt: {
                            $exists : true
                        }
                    }
                }
            });
            dispatch(setArchiveWorkSpace(response.data))
        } catch (error) {
            console.log('error: ', error);
        } finally {
            setLoading(false)
        }
    };

    const restoreWorkspace = async(payload) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.RESTORE,
                prefix: MODULE_ACTIONS.WEB_PREFIX,
                module: MODULES.WORKSPACE,
                common: true,
                parameters: [payload?.slug]
            })
            Toast(response.message); 
            const updatedObj = removeObjectFromArray(archiveWorkspace, payload?._id);
            dispatch(setArchiveWorkSpace(updatedObj));        
            dispatch(setWorkSpaceListAction([...workspaceList, payload]));            
        } catch (error) {
            console.log('error: ', error);
        } finally {
            close()
        } 
    }

    const socketWorkspaceList = async (response) => {
        try {
            if(workspaceList.length) return workspaceList
            dispatch(setWorkSpaceListAction(response))
            const persistWorkspace = decryptedPersist(WORKSPACE);
            const setData = persistWorkspace ? persistWorkspace : response[0];
            dispatch(setSelectedWorkSpaceAction(setData));
        } catch (error) {
            console.log('error: socketWorkspaceList', error);
        }
    };

    return { workspaceList, getList, loading, getArchiveWorkspace, restoreWorkspace, socketWorkspaceList };
};

export default useWorkspaceList;
