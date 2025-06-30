import commonApi from '@/api';
import { APIResponseType } from '@/types/common';
import { FILE, MODULE_ACTIONS } from '@/utils/constant';
import Toast from '@/utils/toast';
import axios, { AxiosProgressEvent } from 'axios';
import React, { useState, useRef, useCallback } from 'react';

type FileDropZoneProps = {
    folder: string;
}

const AUDIO_FILE_TYPES = ['audio/m4a', 'audio/x-m4a'];
const DOCUMENT_FILE_TYPES = ['text/plain'];
const AUDIO_ERROR_MESSAGE = 'File size must be less than 1GB';
const DOCUMENT_ERROR_MESSAGE = 'File size must be less than 5MB';
const AUDIO_ALLOWED_ERROR_MESSAGE = 'Please upload a valid audio file in .m4a format.';
const DOCUMENT_ALLOWED_ERROR_MESSAGE = 'Please upload a valid document in .txt format.';

const useFileDropZone = ({ folder }: FileDropZoneProps) => {
    const [fileLoader, setFileLoader] = useState(false);
    const [fileProgress, setFileProgress] = useState(0);
    const [uploadedFiles, setUploadedFiles] = useState<string[]>([]);
    const [uploadedDocuments, setUploadedDocuments] = useState<string[]>([]);
    const [metadata, setMetadata] = useState<File[]>([]);
    const audioDropRef = useRef<HTMLDivElement>(null);
    const docDropRef = useRef<HTMLDivElement>(null);

    async function generatePresignedUrl(files: File[]): Promise<APIResponseType<string[]>> {
        if (!files.length) return;
        try {
            const response: APIResponseType<string[]> = await commonApi({
                action: MODULE_ACTIONS.GENERATE_PRESIGNED_URL,
                data: {
                    fileKey: files.map((file: File) => {
                        return {
                            key: file.name,
                            type: file.type
                        }
                    }),
                    folder: folder
                }
            });
            return response;
        } catch (error) {
            console.error('Error generating presigned url', error);
        }
    }

    async function fileUploader(files: File[], isDocument: boolean = false) {
        try {
            setFileLoader(true);
            const presignedUrlResponse = await generatePresignedUrl(files);
            if (!presignedUrlResponse.data?.length) return;
            const uploadPromises = files.map((file: File, index: number) => {
                const url = presignedUrlResponse.data[index];
                return axios.put(url, file, {
                    headers: {
                        'Content-Type': file.type
                    },
                    onUploadProgress: (progressEvent: AxiosProgressEvent) => {
                        const rawProgress = Math.round((progressEvent.loaded * 100) / (progressEvent.total ?? 1));
                        const progress = Math.min(Math.round(rawProgress), 99);
                        setFileProgress(progress);
                    }
                });
            });

            const uploadedFiles = await Promise.all(uploadPromises);
            if (isDocument) {
                setUploadedDocuments(uploadedFiles.map(file => {
                    return {
                        url: extractS3Url(file.config.url),
                        name: file.config.data.name,
                        type: file.config.data.type,
                        size: file.config.data.size
                    }
                }));
            } else {
                setUploadedFiles(uploadedFiles.map(file => {
                    return {
                        url: extractS3Url(file.config.url),
                        name: file.config.data.name,
                        type: file.config.data.type,
                        size: file.config.data.size
                    }
                }));
            }
        } catch (error) {
            console.error('Error uploading file', error);
        } finally {
            setFileLoader(false);
            setFileProgress(0);
            setMetadata([]);
        }
    }

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files as File[];
        const fileList = Array.from(files);
        if (fileList.some(file => file.size > FILE.ZOOM_AUDIO_SIZE)) {
            Toast(AUDIO_ERROR_MESSAGE, 'error');
            return;
        }
        if (fileList.some(file => !AUDIO_FILE_TYPES.includes(file.type))) {
            Toast(AUDIO_ALLOWED_ERROR_MESSAGE, 'error');
            return;
        }
        setMetadata(fileList);
        await fileUploader(fileList);
    };

    const handleDocumentChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files as File[];
        const fileList = Array.from(files);
        if (fileList.some(file => file.size > FILE.SIZE)) {
            Toast(DOCUMENT_ERROR_MESSAGE, 'error');
            return;
        }
        if (fileList.some(file => !DOCUMENT_FILE_TYPES.includes(file.type))) {
            Toast(DOCUMENT_ALLOWED_ERROR_MESSAGE, 'error');
            return;
        }
        setMetadata(fileList);
        await fileUploader(fileList, true);
    };

    const extractS3Url = (url: string) => {
        const parsedUrl = new URL(url);
        const fullPath = parsedUrl.pathname;
        return fullPath;
    }

    /**
     * Drag and drop events
     * @param e - The drag event
     * present event bubbling because it affects the chat page drag and drop
     * stop immediate propagation to prevent the event from being handled by the chat page
     * stopImmediatePropagation not directly available in react element so we need to use native event
     */
    const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
    }, []);

    const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
    }, []);

    const handleDrop = useCallback(async (e: React.DragEvent<HTMLDivElement>, isDocument: boolean = false) => {
        e.preventDefault();
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
        const files = Array.from(e.dataTransfer.files ?? []);
        const fileList = Array.from(files as File[]);
        if (isDocument) {
            if (fileList.some(file => file.size > FILE.SIZE)) {
                Toast(DOCUMENT_ERROR_MESSAGE, 'error');
                return;
            }
            if (fileList.some(file => !DOCUMENT_FILE_TYPES.includes(file.type))) {
                Toast(DOCUMENT_ALLOWED_ERROR_MESSAGE, 'error');
                return;
            }
        } else {
            if (fileList.some(file => file.size > FILE.ZOOM_AUDIO_SIZE)) {
                Toast(AUDIO_ERROR_MESSAGE, 'error');
                return;
            }
            if (fileList.some(file => !AUDIO_FILE_TYPES.includes(file.type))) {
                Toast(AUDIO_ALLOWED_ERROR_MESSAGE, 'error');
                return;
            }
        }
        setMetadata(fileList);
        await fileUploader(fileList, isDocument);
    }, []);

    return {
        handleFileChange,
        fileLoader,
        fileProgress,
        uploadedFiles,
        uploadedDocuments,
        handleDocumentChange,
        metadata,
        handleDragOver,
        handleDragEnter,
        handleDragLeave,
        handleDrop,
        audioDropRef,
        docDropRef
    }
}

export default useFileDropZone