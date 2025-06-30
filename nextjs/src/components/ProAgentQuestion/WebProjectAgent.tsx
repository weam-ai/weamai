import Customgpt from '@/icons/Customgpt';
import GlobeIcon from '@/icons/GlobalIcon';
import { WebProjectProposalFormType } from '@/types/proAgents';
import React from 'react'

type WebProjectAgentProps = {
    proAgentData: WebProjectProposalFormType;
}

const questionKeys = {
    clientName: 'Client Name',
    description: 'Description',
    discussionDate: 'Discussion Date',
    submittedBy: 'Submitted By',
    designation: 'Designation',
    companyName: 'Company Name',
    submissionDate: 'Submission Date',
    mobile: 'Mobile',
    email: 'Email',
    companyLocation: 'Company Location',
}

const WebProjectAgent = ({ proAgentData }: WebProjectAgentProps) => {
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
            Project Name: {proAgentData.projectName}
        </div>
        {
            Object.keys(proAgentData).reduce((acc, key) => {
                if (questionKeys[key]) {
                    acc.push(
                        <div className='text-font-14 text-b5' key={key}>
                            <span className="text-b2 font-medium">{questionKeys[key]}:</span> {proAgentData[key]}
                        </div>
                    )
                }
                return acc;
            }, [])
        }
    </>
    )
}

export default WebProjectAgent