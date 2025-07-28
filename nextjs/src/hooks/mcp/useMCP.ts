import { useDispatch, useSelector } from 'react-redux';
import { RootState } from '@/lib/store';
import {
    setToolStatesAction,
    updateToolStatesAction,
    addToolToMCPAction,
    removeToolFromMCPAction,
    clearMCPToolsAction,
    setSelectedMcpAction,
    setIsConnectedAction,
    setMCPLoadingAction,
    resetMCPAction,
    persistToolStatesAction,
    setMCPDataAction,
    updateMCPDataEntryAction,
    removeMCPDataEntryAction
} from '@/lib/slices/mcpSlice';

const useMCP = () => {
    const dispatch = useDispatch();
    const toolStates = useSelector((store: RootState) => store.mcp.toolStates);
    const selectedMcp = useSelector((store: RootState) => store.mcp.selectedMcp);
    const isConnected = useSelector((store: RootState) => store.mcp.isConnected);
    const loading = useSelector((store: RootState) => store.mcp.loading);
    const mcpdata = useSelector((store: RootState) => store.mcp.mcpdata);

    const setToolStates = (toolStates: Record<string, string[]>) => {
        dispatch(setToolStatesAction(toolStates));
    };

    const updateToolStates = (mcpCode: string, tools: string[]) => {
        dispatch(updateToolStatesAction({ mcpCode, tools }));
    };

    const addToolToMCP = (mcpCode: string, tool: string) => {
        dispatch(addToolToMCPAction({ mcpCode, tool }));
    };

    const removeToolFromMCP = (mcpCode: string, tool: string) => {
        dispatch(removeToolFromMCPAction({ mcpCode, tool }));
    };

    const clearMCPTools = (mcpCode: string) => {
        dispatch(clearMCPToolsAction(mcpCode));
    };

    const setSelectedMcp = (mcp: Record<string, any>) => {
        dispatch(setSelectedMcpAction(mcp));
    };

    const setIsConnected = (connected: boolean) => {
        dispatch(setIsConnectedAction(connected));
    };

    const setMCPLoading = (loading: boolean) => {
        dispatch(setMCPLoadingAction(loading));
    };

    const resetMCP = () => {
        dispatch(resetMCPAction());
    };

    const persistToolStates = () => {
        dispatch(persistToolStatesAction());
    };

    const setMCPData = (data: Record<string, any>) => {
        dispatch(setMCPDataAction(data));
    };

    const updateMCPDataEntry = (key: string, data: any) => {
        dispatch(updateMCPDataEntryAction({ key, data }));
    };

    const removeMCPDataEntry = (key: string) => {
        dispatch(removeMCPDataEntryAction(key));
    };

    return {
        toolStates,
        selectedMcp,
        isConnected,
        loading,
        mcpdata,
        setToolStates,
        updateToolStates,
        addToolToMCP,
        removeToolFromMCP,
        clearMCPTools,
        setSelectedMcp,
        setIsConnected,
        setMCPLoading,
        resetMCP,
        persistToolStates,
        setMCPData,
        updateMCPDataEntry,
        removeMCPDataEntry
    };
};

export default useMCP; 