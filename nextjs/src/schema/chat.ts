import * as yup from 'yup';

export const forkChatSchema = yup.object({
    type: yup.object().nullable().required('please select brain'),
})

export const importChatSchema = yup.object({
    code: yup.string().required('Please select platform'),
    file: yup.mixed()
        .required('Please upload file')
        .test('fileType', 'Only JSON files are allowed', (value: File) => {
            if (!value) return false;
            return value?.type === 'application/json' || value?.name?.endsWith('.json');
        })
        .test('fileName', 'File name must be conversations.json', (value: File) => {
            if (!value) return false;
            return value.name.startsWith('conversations') && value.name.endsWith('.json');
        })
        .test('fileSize', 'File size must be less than 512MB', (value: File) => {
            if (!value) return false;
            const maxSize = 512 * 1024 * 1024; // 512MB in bytes
            return value.size <= maxSize;
        })
        .test('singleFile', 'Only one file is allowed', (value) => {
            if (Array.isArray(value)) {
                return value.length === 1;
            }
            return value instanceof File;
        }),
})

export type ForkChatSchemaType = yup.InferType<typeof forkChatSchema>;
export type ImportChatSchemaType = yup.InferType<typeof importChatSchema>;
