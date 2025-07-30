import ProIcon from "@/icons/ProIcon";
import { ProAgentCode, ProAgentComponentLable } from '@/types/common';
import { getModelCredit } from "@/utils/helper";

const ProAgentList = ({handleAgentFormClick}:any) => {
    const buttonList = [
        {
            label: 'QA Specialist',
            information: 'The agent for website QA—click to analyze, instantly get your website\'s results, and detect bugs!',
            onClickValue: ProAgentComponentLable.QA,
            code: ProAgentCode.QA_SPECIALISTS
        },
        {
            label: 'SEO Optimised Articles',
            information: 'Generate articles for your website with this agent—it creates SEO-friendly content and suggests keywords to boost your rankings!',
            onClickValue: ProAgentComponentLable.SEO,
            code: ProAgentCode.SEO_OPTIMISED_ARTICLES
        },
        // {
        //     label: 'CV Screening Specialist',
        //     information: 'Use this agent to meet your companys hiring needs and find the perfect resource, streamlining your recruitment process!',
        //     onClickValue: ProAgentComponentLable.HR
        // },
        {
            label: 'Client Video Call Analyzer',
            information: 'Use this agent to review the client call and summarize the meeting.',
            onClickValue: ProAgentComponentLable.CALL,
            code: ProAgentCode.VIDEO_CALL_ANALYZER,
        },
        {
            label: 'Web Project Proposal',
            information: 'Create a compelling web project proposal with this agent and seamlessly onboard your client!',
            onClickValue: ProAgentComponentLable.PROJECT,
            code: ProAgentCode.WEB_PROJECT_PROPOSAL
        },
        {
            label: 'Sales Call Analyzer',
            information: 'Use this agent to analyze your team sales calls and gain valuable insights to improve performance!',
            onClickValue: ProAgentComponentLable.SALES,
            code: ProAgentCode.SALES_CALL_ANALYZER
        },
    ]

    return (    
        <>
            {buttonList.map((button, index) => (
                <div key={index} className="cursor-pointer border-b py-4 px-2.5 transition-all ease-in-out hover:bg-b13 bg-white border-b10 flex-wrap"
                    onClick={() => handleAgentFormClick(button.onClickValue)}>
                    <div className="flex items-center flex-wrap">
                            <ProIcon 
                            width={'16'}
                            height={'16'}
                            className="mr-2 fill-orange group-data-[state=active]:fill-b2" />
                        <p className="text-font-12 font-medium text-b2">{button.label}</p>
                        <span className="text-font-12 ml-2 px-2 py-[2px] bg-b13 border rounded-full max-md:hidden">Pro</span>
                        <div className="ml-auto">
                            <span className="text-font-12 px-2 max-md:px-1 py-[2px] bg-white border rounded-md">Credits: {getModelCredit(button?.code)}</span>
                        </div>
                        
                    </div>
                    <p className="text-font-12 font-normal text-b6 mt-1">
                        {button.information} 
                    </p>                
                </div>
            ))}
        </>
    )
}

export default ProAgentList;