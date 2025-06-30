import Customgpt from "@/icons/Customgpt";
import GlobeIcon from "@/icons/GlobalIcon";
import { SEOAgentStep1Type, SEOAgentStep2Type, SEOAgentStep3Type, SEOAgentStep4Type } from '@/types/chat';
import { ProAgentCode } from '@/types/common';
import { SelectOption } from '@/types/proAgents';

type SEOProAgentQueProps = {
    proAgentData: {
        code: ProAgentCode.SEO_OPTIMISED_ARTICLES;
        audience: string;
        keywords: string[];
        location: SelectOption[];
        projectName: string;
        step1?: SEOAgentStep1Type;
        step2?: SEOAgentStep2Type;
        step3?: SEOAgentStep3Type;
        step4?: SEOAgentStep4Type;
        summary: string;
        url: string;
    }
}

const questionKeys: Record<keyof Pick<SEOProAgentQueProps['proAgentData'], 'keywords' | 'audience' | 'summary'>, string> = {
    keywords: 'Targeted Keywords',
    audience: 'Target Audience',
    summary: 'Business Summary',
}

const SEOProAgentQue = ({ proAgentData }: SEOProAgentQueProps) => {
    return (
        <>
            <p className='text-font-14 font-bold flex items-center gap-x-1'>
                <Customgpt
                    width={'16'}
                    height={'16'}
                    className="mr-2 fill-b5 group-data-[state=active]:fill-b2"
                />
                Agent: {proAgentData?.code?.replace(/_/g, ' ')}
            </p>
            <div className='text-font-14 flex items-center gap-x-1'>
                <GlobeIcon
                    width={'16'}
                    height={'16'}
                    className="mr-2 fill-b5"
                />
                URL: {proAgentData?.url}
            </div>
            <div className='text-font-14 mt-3 font-bold'>
                Project Name: {proAgentData?.projectName}
            </div>
            {
                proAgentData?.step3?.primary_keywords?.length > 0 && (
                    <div className='text-font-14 text-b5'>
                        <span className="text-b2 font-medium">Primary Keywords:</span> {proAgentData?.step3?.primary_keywords?.map((keyword) => keyword).join(', ')}
                    </div>
                )
            }
            {proAgentData?.step3?.secondary_keywords?.length > 0 && (
                <div className='text-font-14 text-b5'>
                    <span className="text-b2 font-medium">Secondary Keywords:</span> {proAgentData?.step3?.secondary_keywords?.map((keyword) => keyword).join(', ')}
                </div>
            )}
            {
                Object.keys(questionKeys).map((key, index) => {
                    if (key === 'location') {
                        return (
                            <div className='text-font-14 text-b5' key={key}>
                                <span className="text-b2 font-medium">Location:</span> {proAgentData?.location?.map((location) => location.label).join(', ')}
                            </div>
                        )
                    }
                    return (
                        <div className='text-font-14 text-b5' key={index}>
                            <span className="text-b2 font-medium">{questionKeys[key]}:</span> {Array.isArray(proAgentData[key]) ? proAgentData[key].join(', ') : proAgentData[key]}
                        </div>
                    )
                })
            }
        </>
    );
}

export default SEOProAgentQue;