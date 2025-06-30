import React from 'react';
import { TabsContent } from '@/components/ui/tabs';
import CustomPromptList from './CustomPromptList';
import CustomPromptAction from '@/actions/CustomPromptAction';

const CustomPrompts = async () => {

    const defaultprompts = await CustomPromptAction('',null);

    return (
        <TabsContent value="prompttemplate">
            <div className="w-full mt-5">
                <CustomPromptList defaultprompts={defaultprompts} />                                                      
            </div>
        </TabsContent>
    );
};

export default CustomPrompts;
