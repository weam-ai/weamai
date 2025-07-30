import React, { useMemo, useState } from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogTrigger } from '@/components/ui/dialog'
import MCP_OPTIONS from '@/components/Mcp/MCPAppList';
import ConnectedAppSelection from '@/components/Mcp/ConnectedAppCard';
import { useSelector } from 'react-redux';
import { RootState } from '@/lib/store';

type MCPDialogAppListProps = {
    dialogTriggerTitle: string;
}

export const MCPDialogAppList = ({ dialogTriggerTitle }: MCPDialogAppListProps) => {

    const [mcpSearch, setMcpSearch] = useState('');
    const filteredApps = useMemo(() => {
        if (!mcpSearch) return MCP_OPTIONS;
        return MCP_OPTIONS.filter(
            (app) =>
                app.title.toLowerCase().includes(mcpSearch.toLowerCase()) ||
                app.description.toLowerCase().includes(mcpSearch.toLowerCase())
        );
    }, [mcpSearch]);

    const mcpData = useSelector((state: RootState) => state.mcp.mcpdata);
    
  return (
    <Dialog>
    <DialogTrigger asChild>
        <div className='flex cursor-pointer items-center pt-3 pb-2 rounded-b-lg'>
            <p className='text-font-14'>{dialogTriggerTitle}</p>
        </div>
    </DialogTrigger>
    
    <DialogContent className="md:max-w-[900px] max-w-[calc(100%-30px)] py-7">
        <DialogHeader className="rounded-t-10 px-[30px] pb-5 border-b">
            <DialogTitle className="font-semibold text-font-20 flex items-center">Connections</DialogTitle>
            <DialogDescription>
                Unlock more with Weam when you connect these reviewed and recommended tools.
            </DialogDescription>
        </DialogHeader>
        <div className="px-5 md:px-10 py-5 rounded-b-10">
            <div className="flex items-center">
                <div className="w-80 ml-auto relative">
                    {/* <SearchIcon
                        width={20}
                        height={20}
                        className="fill-b5 w-4 h-auto absolute left-3 top-1/2 translate-y-[-50%]"
                    />
                    <SearchInput
                        value={mcpSearch}
                        onChange={e => setMcpSearch(e.target.value)}
                    /> */}
                </div> 
            </div>
            <ConnectedAppSelection filteredApps={filteredApps} fromDialog={true} mcpData={mcpData} />
        </div>
    </DialogContent>
</Dialog>
  )
}
