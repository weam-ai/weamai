import React from 'react';
import { TabsContent } from '@/components/ui/tabs';
import CustomBotList from './CustomBotList';
import CustomBotAction from '@/actions/CustomTemplateAction';

const CustomBots = async () => {

    const defaultbots = await CustomBotAction('');

    return (
        <TabsContent value="bottemplate">
            <div className="w-full mt-5">
                <CustomBotList defaultbots={defaultbots} />                
            </div>
        </TabsContent>
    );
};

export default CustomBots;

