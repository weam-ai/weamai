'use client';
import React from 'react';
import { Switch } from '../ui/switch';
import DownArrowIcon from '@/icons/DownArrow';
import RightArrow from '@/icons/RightArrow';

type ConnectedAppMiniCardProps = {
    icon: React.ReactNode;
    mcpTitle: string;
    mcpCode: string;
    tools: string[];
    isSubmenuOpen?: boolean;
    toolStates: Record<string, string[]>;
    onAction: (action: 'toggleSubmenu' | 'toggleTool' | 'toggleApp', mcpCode: string, tools?: string[], toolName?: string, checked?: boolean) => void;
};

const ConnectedAppMiniCard: React.FC<ConnectedAppMiniCardProps> = ({
    icon,
    mcpTitle,
    mcpCode,
    tools,
    isSubmenuOpen = false,
    toolStates,
    onAction
}) => {
    const handleToggleSubmenu = (e: React.MouseEvent) => {
        e.stopPropagation();
        onAction('toggleSubmenu', mcpCode, tools);
    };

    const handleToolToggle = (toolName: string, checked: boolean) => {
        onAction('toggleTool', mcpCode, tools, toolName, checked);
    };

    const handleCardClick = () => {
        if (tools.length > 0) {
            onAction('toggleSubmenu', mcpCode, tools);
        }
    };

    // Check if any tool is enabled for this specific MCP app
    const currentAppTools = toolStates[mcpCode] || [];
    const isCurrentAppToolEnabled = currentAppTools.length > 0;

    const handleAppToggle = (checked: boolean) => {
        onAction('toggleApp', mcpCode, tools, undefined, checked);
    };

    return (
        <div className='border-b py-1'>
            <div
                className="flex items-center gap-x-2 cursor-pointer hover:bg-gray-100 rounded-md p-1.5"
                onClick={handleCardClick}
            >
                <div className="size-4 flex items-center justify-center">
                    {icon}
                </div>
                <h3 className="text-font-14">{mcpTitle}</h3>
            </div> 
        </div>
    );
};

export default ConnectedAppMiniCard;
