import React, { memo } from 'react';
import { ProAgentCode } from '@/types/common';
import QAProAgentQue from '../ProAgentQuestion/QAProAgentQue';
import SEOProAgentQue from '../ProAgentQuestion/SEOProAgentQue';
import WebProjectAgent from '../ProAgentQuestion/WebProjectAgent';
import VideoCallAgent from '../ProAgentQuestion/VideoCallAgent';
import SalesCallAgentQue from '../ProAgentQuestion/SalesCallAgentQue';

const ProAgentQuestion = memo(({ proAgentData }) => {
    let content;
    switch (proAgentData?.code) {
        case ProAgentCode.QA_SPECIALISTS:
            content = <QAProAgentQue code={proAgentData.code} url={proAgentData.url} />;
            break;
        case ProAgentCode.SEO_OPTIMISED_ARTICLES:
            content = <SEOProAgentQue proAgentData={proAgentData} />;
            break;
        case ProAgentCode.WEB_PROJECT_PROPOSAL:
            content = <WebProjectAgent proAgentData={proAgentData} />;
            break;
        case ProAgentCode.VIDEO_CALL_ANALYZER:
            content = <VideoCallAgent proAgentData={proAgentData} />;
            break;
        case ProAgentCode.SALES_CALL_ANALYZER:
            content = <SalesCallAgentQue proAgentData={proAgentData} />;
            break;
        default:
            content = '';
    }

    return content;
});  

export default ProAgentQuestion;