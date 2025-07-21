import { EMAIL_REGEX_MESSAGE, INVALID_EMAIL_MESSAGE } from '@/utils/constant';
import { REGEX } from '@/utils/helper';
import * as yup from 'yup';

const urlRegex = /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(\/\S*)?$/;
const WEBSITE_URL_ERROR_MESSAGE = 'Please provide a valid website URL.';
const phoneRegex = /^\+(?:[0-9] ?){6,14}[0-9]$/;

const DEBOUNCE_WAIT = 1000;
let debounceTimeout: NodeJS.Timeout | null = null;
let lastPromiseReject: ((reason?: unknown) => void) | null = null;

export const debouncedUrlCheck = (value: string): Promise<boolean> => {
    return new Promise((resolve, reject) => {
        if (debounceTimeout) clearTimeout(debounceTimeout);
        if (lastPromiseReject) lastPromiseReject('debounced');
        lastPromiseReject = reject;

        debounceTimeout = setTimeout(async () => {
            try {
                const urlToCheck = value.startsWith('http') ? value : `https://${value}`;

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 2000);

                try {
                    await fetch(urlToCheck, {
                        method: 'HEAD',
                        mode: 'no-cors',
                        signal: controller.signal,
                    });
                    resolve(true);
                } catch (e) {
                    resolve(false);
                } finally {
                    clearTimeout(timeoutId);
                }
            } catch (err) {
                resolve(false);
            }
        }, DEBOUNCE_WAIT);
    });
};

export const qaSpecialistSchema = yup.object({
    url: yup
        .string()
        .required('Website URL is required.')
        .matches(urlRegex, WEBSITE_URL_ERROR_MESSAGE),
});

export const seoAiKeywordSchema = yup.object({
    projectName: yup.string().max(59, 'Project name must be less than 60 characters.').required('Project name is required.'),
    keywords: yup.array().of(
        yup.string().required('Keyword is required.')
    ).min(1, 'Please select at least one keyword.'),
    location: yup.array().of(
        yup.object().shape({
            value: yup.string().required('Location is required.'),
            label: yup.string().required('Location is required.'),
        })
    ).min(1, 'Please select at least one location.'),
    url: yup
        .string()
        .required('Website URL is required.')
        .matches(urlRegex, WEBSITE_URL_ERROR_MESSAGE),
});

export const seoAgentSchema = yup.object({
    ...seoAiKeywordSchema.fields,
    audience: yup.string().required('Audience is required.'),
    summary: yup.string().required('Summary is required.'),
});

export const seoTopicGenerationSchema = yup.object({
    topic: yup.string().required('Topic is required.'),
});

export const webProposalAgentSchema = yup.object({
    clientName: yup.string().max(59, 'Client name must be less than 60 characters.').required('Client name is required.'),
    projectName: yup.string().max(59, 'Project name must be less than 60 characters.').required('Project name is required.'),
    description: yup.string().required('Project description is required.'),
    discussionDate: yup.date().required('Discussion date is required.'),
    submissionDate: yup.date().required('Submission date is required.'),
    submittedBy: yup.string().required('Submitted by is required.'),
    designation: yup.string().required('Designation is required.'),
    companyName: yup.string().max(59, 'Company name must be less than 60 characters.').required('Company name is required.'),
    url: yup
        .string()
        .required('Website URL is required.')
        .matches(urlRegex, WEBSITE_URL_ERROR_MESSAGE),
    mobile: yup
        .string()
        .trim()
        .required('Mobile number is required.')
        .matches(phoneRegex, 'Enter a valid mobile number.'),
    email: yup
        .string()
        .required(EMAIL_REGEX_MESSAGE)
        .test(
            'valid-email',
            INVALID_EMAIL_MESSAGE,
            (email) => {
                const emailRegex = REGEX.EMAIL_DOMAIN_REGEX;
                const result = email ? emailRegex.test(email) : true;
                return result;
            }
        ),
    location: yup.string().required('Location is required.'),
});

export const videoCallSchema = yup.object({
    url: yup
        .string()
        .required('Website URL is required.'),
    prompt: yup.string().required('Prompt is required.'),
});

export type QaSpecialistSchemaType = yup.InferType<typeof qaSpecialistSchema>;
export type SeoAgentSchemaType = yup.InferType<typeof seoAgentSchema>;
export type SeoAiKeywordSchemaType = yup.InferType<typeof seoAiKeywordSchema>;
export type SeoTopicGenerationSchemaType = yup.InferType<typeof seoTopicGenerationSchema>;
export type WebProposalAgentSchemaType = yup.InferType<typeof webProposalAgentSchema>;
export type VideoCallSchemaType = yup.InferType<typeof videoCallSchema>;