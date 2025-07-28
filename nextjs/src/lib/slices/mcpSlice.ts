import { createSlice } from '@reduxjs/toolkit';
import { MCP_CODES } from '@/components/Mcp/MCPAppList';
import { retrieveMCPToolStates, persistMCPToolStates } from '@/utils/helper';

type MCPToolState = Record<string, string[]>;

interface MCPState {
    toolStates: MCPToolState;
    selectedMcp: Record<string, any>;
    isConnected: boolean;
    loading: boolean;
    mcpdata: Record<string, any>;
}

// Get persisted tool states or use default
const getInitialToolStates = (): MCPToolState => {
    const persistedStates = retrieveMCPToolStates();
    if (persistedStates) {
        return persistedStates;
    }
    
    return {
        [MCP_CODES.SLACK]: [],
        [MCP_CODES.GITHUB]: [],
        [MCP_CODES.GOOGLE_CALENDAR]: [],
        [MCP_CODES.GMAIL]: [],
        [MCP_CODES.GOOGLE_DRIVE]: [],
    };
};

const initialState: MCPState = {
    toolStates: getInitialToolStates(),
    selectedMcp: {},
    isConnected: false,
    loading: false,
    mcpdata: {}
};

const mcpSlice = createSlice({
    name: 'mcp',
    initialState,
    reducers: {
        setToolStatesAction: (state, action) => {
            state.toolStates = action.payload;
            persistMCPToolStates(action.payload);
        },
        updateToolStatesAction: (state, action) => {
            const { mcpCode, tools } = action.payload;
            state.toolStates[mcpCode] = tools;
            persistMCPToolStates(state.toolStates);
        },
        addToolToMCPAction: (state, action) => {
            const { mcpCode, tool } = action.payload;
            if (!state.toolStates[mcpCode]) {
                state.toolStates[mcpCode] = [];
            }
            if (!state.toolStates[mcpCode].includes(tool)) {
                state.toolStates[mcpCode].push(tool);
            }
            persistMCPToolStates(state.toolStates);
        },
        removeToolFromMCPAction: (state, action) => {
            const { mcpCode, tool } = action.payload;
            if (state.toolStates[mcpCode]) {
                state.toolStates[mcpCode] = state.toolStates[mcpCode].filter(t => t !== tool);
            }
            persistMCPToolStates(state.toolStates);
        },
        clearMCPToolsAction: (state, action) => {
            const mcpCode = action.payload;
            state.toolStates[mcpCode] = [];
            persistMCPToolStates(state.toolStates);
        },
        setSelectedMcpAction: (state, action) => {
            state.selectedMcp = action.payload;
        },
        setIsConnectedAction: (state, action) => {
            state.isConnected = action.payload;
        },
        setMCPLoadingAction: (state, action) => {
            state.loading = action.payload;
        },
        resetMCPAction: (state) => {
            state.toolStates = initialState.toolStates;
            state.selectedMcp = {};
            state.isConnected = false;
            state.loading = false;
            state.mcpdata = {};
            persistMCPToolStates(state.toolStates);
        },
        persistToolStatesAction: (state) => {
            persistMCPToolStates(state.toolStates);
        },
        setMCPDataAction: (state, action) => {
            state.mcpdata = { ...state.mcpdata, ...action.payload };
        },
        updateMCPDataEntryAction: (state, action) => {
            const { key, data } = action.payload;
            state.mcpdata[key] = data;
        },
        removeMCPDataEntryAction: (state, action) => {
            const key = action.payload;
            delete state.mcpdata[key];
        }
    }
});

export const {
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
} = mcpSlice.actions;

export default mcpSlice.reducer; 