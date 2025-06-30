import { ProAgentCode } from "./common";

export type SelectOption = {
    value: string;
    label: string;
}

export type BusinessSummaryPayloadType = {
    projectName: string;
    keywords: string[];
    location: SelectOption[];
    url: string;
};

export type BusinessSummaryResponseType = {
    business_summary: string;
    target_audience: string;
}

export type SeoTopicGenerationPayloadType = {
    messageId: string;
    secondaryKeywords: string[];
    primaryKeyword: string;
}

export type SeoTopicGenerationResponseType = {
    topics: string;
}

export type Step1 = {
    business_summary: string;
    target_audience:  string;
    target_keywords:  string[];
    website:          string;
    language:         string;
    location:         string[];
}

export type EdVolume = {
    id:            string;
    keyword:       string;
    search_volume: number;
    competition:   null | string;
}

export type Step2 = {
    targeted_volumes:    EdVolume[];
    recommended_volumes: EdVolume[];
}

export type Step3 = {
    topics:            string;
    selected_keywords: string[];
}

export type ProAgentDataResponseType = {
    code:        string;
    url:         string;
    projectName: string;
    keywords:    string[];
    language:    SelectOption;
    location:    SelectOption[];
    audience:    string;
    summary:     string;
    step1:       Step1;
    step2:       Step2;
    step3:       Step3;
}

export type keywordCheckBoxType = {
    competition: string;
    keyword: string;
    search_volume: number;
    id: string;
}

export type SeoArticlePayloadType = {
    messageId: string;
    topicName: string;
    chatId: string;
}

export type WebProjectProposalFormType = WebProjectProposalExtraInfoType & {
    code: ProAgentCode.WEB_PROJECT_PROPOSAL;
    url: string;
}

export type WebProjectProposalExtraInfoType = {
    clientName?: string;
    projectName?: string;
    description?: string;
    discussionDate?: string;
    submittedBy?: string;
    designation?: string;
    companyName?: string;
    submissionDate?: string;
    mobile?: string;
    email?: string;
    companyLocation?: string;
    file?: string;
    user_prompt?: string;
}

export enum SALES_CALL_ANALYZER_API_CODE {
    AUDIO = 'AUDIO',
    DOC = 'DOC',
    URL = 'URL',
    FATHOM = 'FATHOM',
    TRANSCRIPT = 'TRANSCRIPT',
}

export type SalesCallPayloadType = {
    messageId: string;
    chatId: string;
    text: string;
    service_code: string;
    product_summary_code: string;
    product_info: string;
    prompt: string;
    msgCredit: number;
}