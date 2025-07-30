import Customgpt from '@/icons/Customgpt';
import GlobeIcon from '@/icons/GlobalIcon';
import { ProAgentDataType } from '@/types/chat';
import { SALES_CALL_ANALYZER_API_CODE } from '@/types/proAgents';
import React from 'react';

type SalesCallAgentQueProps = {
    proAgentData: ProAgentDataType;
};

type InfoItemProps = {
    icon?: React.ReactNode;
    label: string;
    value: string;
};

const ICON_SIZE = '16';
const ITEM_CLASS = 'text-font-14 flex items-center max-md:flex-wrap';

const InfoItem = ({ icon, label, value }: InfoItemProps) => (
    <div className={ITEM_CLASS}>
        {icon && <span className="mr-2">{icon}</span>}
        <span className="font-medium">{label}:</span> {value}
    </div>
);

const SalesCallAgentQue = ({ proAgentData }: SalesCallAgentQueProps) => {
    return (
        <>
            <div className="flex ">
                <Customgpt
                    width={'20'}
                    height={'20'}
                    className="mr-2 mt-0.5 fill-b5 group-data-[state=active]:fill-b2"
                />
                <p className="text-font-14 font-bold flex items-center gap-x-1">
                    Agent: {proAgentData?.code?.replace(/_/g, ' ')}
                </p>
            </div>

            <div className="mt-2 ml-7">
                {proAgentData?.audio_url !== '' &&
                    proAgentData?.audio_url.startsWith('http') && (
                        <InfoItem
                            icon={
                                <GlobeIcon
                                    width={ICON_SIZE}
                                    height={ICON_SIZE}
                                    className="fill-b5"
                                />
                            }
                            label="URL"
                            value={proAgentData?.audio_url}
                        />
                    )}
                {proAgentData.product_info &&
                    proAgentData.product_summary_code ===
                        SALES_CALL_ANALYZER_API_CODE.URL && (
                        <InfoItem
                            label="Company URL"
                            value={proAgentData.product_info}
                        />
                    )}
                {proAgentData.audio_url !== '' &&
                    proAgentData.service_code === SALES_CALL_ANALYZER_API_CODE.TRANSCRIPT && (
                        <InfoItem
                            label="Transcript"
                            value={proAgentData.audio_url}
                        />
                    )}
                {proAgentData.audio_file_metadata?.length > 0 && (
                    <InfoItem
                        label="Zoom File"
                        value={proAgentData.audio_file_metadata
                            .map((file) => file.name)
                            .join(', ')}
                    />
                )}
                {proAgentData.document_file_metadata?.length > 0 && (
                    <InfoItem
                        label="Document File"
                        value={proAgentData.document_file_metadata
                            .map((file) => file.name)
                            .join(', ')}
                    />
                )}
            </div>
        </>
    );
};

export default SalesCallAgentQue;
