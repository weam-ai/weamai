'use client';
import React from 'react';
import Image from 'next/image';
import Close from '@/icons/Close';
import { LINK } from '@/config/config';
import { getDocType } from '@/utils/common';
import { DynamicImage } from '@/widgets/DynamicImage';
import { UploadedFileType } from '@/types/chat';
import { extractFileType, getDisplayModelName } from '@/utils/helper';

type UploadFileInputProps = {
    fileData: UploadedFileType[];
    removeFile: (index: number) => void;
}

type RenderAgentProps = {
    agentData: UploadedFileType;
    removeFile: (index: number) => void;
    index: number;
}

type RenderImageAndDocumentsProps = {
    file: UploadedFileType;
    removeFile: (index: number) => void;
    index: number;
}

type RenderAgentAndDocumentProps = UploadFileInputProps;

type FileViewProps = {
    name: string;
    type: string;
    isCustomGpt: undefined | boolean;
    uri: string;
}

type RenderPromptProps = {
    promptData: UploadedFileType;
    removeFile: (index: number) => void;
    index: number;
}

export const DEEPSEEK_WORD = 'deepseek';
export const LLAMA4_WORD = 'llama4';
export const META_LLAMA4_WORD = 'meta-llama';

export const getResponseModel = (responseModel: string) => {
    if (responseModel.startsWith(DEEPSEEK_WORD)) {
        return responseModel.split(':')[0].split('/')?.[1] || responseModel;
    }
    if (responseModel.startsWith(LLAMA4_WORD) || responseModel.startsWith(META_LLAMA4_WORD)) {
        return responseModel.split(':')[0].split('/')?.[1] || responseModel;
    }
    return responseModel;
}

export const attachDeepSeekModel = (model: string) => {
    if (model.startsWith(DEEPSEEK_WORD)) {
        const name = DEEPSEEK_WORD + '/';
        return name + model.slice(0);
    }
    return model;
}

const FileView = ({ name, type, isCustomGpt, uri }: FileViewProps) => {
    return (
        <>
            <div className="attach-img w-5 min-w-5 h-auto rounded-custom overflow-hidden">
                {isCustomGpt ? (
                    <Image
                        src={`${uri}`}
                        alt="Preview"
                        width={20}
                        height={20}
                        className="size-5 object-contain rounded fill-blue"
                    />
                ) : (
                    getDocType(type)
                )}
            </div>
            <div className="attach-item-content">
                <span className="block text-b2 text-font-12 font-bold overflow-hidden whitespace-nowrap text-ellipsis max-w-[180px]">
                    {name}
                </span>
                <span className="text-font-12 text-b8">{extractFileType(type)}</span>
            </div>
        </>
    );
};

export function renderFilePreview(fileData: UploadedFileType) {
    if (!fileData) return null;

    const isImage =
        fileData.mime_type?.startsWith('image/') ||
        fileData.type?.startsWith('image/') ||
        fileData.isCustomGpt;

    if (isImage) {
        const imageUrl = fileData.isCustomGpt
            ? fileData.uri
            : fileData instanceof File
            ? URL.createObjectURL(fileData)
            : `${LINK.AWS_S3_URL}${fileData.uri}`;

        return (
            <DynamicImage
                src={imageUrl}
                alt={fileData.name}
                width={40}
                height={40}
                className="size-10 object-contain rounded"
                placeholder='blur'
            />
        );
    } else {
        return (
            <FileView
                name={fileData.name}
                type={fileData.type}
                isCustomGpt={fileData.isCustomGpt}
                uri={fileData.uri}
            />
        );
    }
}

const RenderAgent = ({ agentData, removeFile, index }: RenderAgentProps) => {
    if (!agentData) return null;
    return (
        <div className="attach-item flex flex-wrap items-center gap-2 group/item relative w-full p-2 rounded-[10px] border-b-2">
            <span
                className="lg:opacity-0 group-hover/item:opacity-100 lg:invisible group-hover/item:visible absolute top-0.5 right-0.5 cursor-pointer p-1"
                onClick={() => removeFile(index)}
            >
                <Close
                    width={'8'}
                    height={'8'}
                    className="fill-b7 size-2 object-contain"
                />
            </span>
            <DynamicImage
                src={agentData.gptCoverImage}
                alt="Preview"
                width={40}
                height={40}
                className="size-10 object-contain rounded"
                placeholder="blur"
            />
            <p className="text-font-14">{agentData.gptname}</p>
            <p className="block text-font-14 text-b2 bg-b12 px-2 py-[2px] rounded-lg">
                {getDisplayModelName(agentData?.responseModel)}
            </p>
        </div>
    );
};

const RenderImageAndDocuments = ({ file, removeFile, index }: RenderImageAndDocumentsProps) => {
    return (
        <div
            key={index}
            className="attach-item flex flex-1 items-center gap-2 group/item relative w-full p-2 rounded-[10px] border-b-2"
        >
            <span
                className="opacity-0 group-hover/item:opacity-100 invisible group-hover/item:visible absolute top-0.5 right-0.5 cursor-pointer p-1"
                onClick={() => removeFile(index)}
            >
                <Close
                    width={'8'}
                    height={'8'}
                    className="fill-b7 size-2 object-contain"
                />
            </span>
            {file.mime_type?.startsWith('image/') ? (
                <>
                    <DynamicImage
                        src={`${LINK.AWS_S3_URL}${file.uri}`}
                        alt="Preview"
                        width={40}
                        height={40}
                        className="size-10 object-contain rounded"
                        placeholder="blur"
                    />
                    <p className="text-font-14">{file.gptname || file.name}</p>
                    <p className="block text-font-14 text-b2 bg-b12 px-2 py-[2px] rounded-lg">
                        {file?.responseModel || extractFileType(file.mime_type)}
                    </p>
                </>
            ) : (
                <FileView
                    name={file.name}
                    type={file.mime_type || file.type}
                    isCustomGpt={file.isCustomGpt}
                    uri={file.uri}
                />
            )}
        </div>
    );
};

const RenderPrompt = ({ promptData, removeFile, index }: RenderPromptProps) => {
    if (!promptData) return null;
    return (
        <div className="attach-item flex flex-wrap items-center gap-2 group/item relative w-full p-2 rounded-[10px] border-b-2">
            <span
                className="opacity-0 group-hover/item:opacity-100 invisible group-hover/item:visible absolute top-0.5 right-0.5 cursor-pointer p-1"
                onClick={() => removeFile(index)}
            >
                <Close
                    width={'8'}
                    height={'8'}
                    className="fill-b7 size-2 object-contain"
                />
            </span>
            <div>
                <p>{promptData.name}</p>
            </div>
        </div>
    );
};

const RenderAgentAndDocument = ({ fileData, removeFile }: RenderAgentAndDocumentProps) => {
    return (
        <div className="attached-files p-2">
            <div className="flex gap-2 flex-wrap">
                {fileData?.length > 0 && (
                    <>
                        {
                            fileData.map((file: UploadedFileType, index: number) => (
                                <React.Fragment key={index}>
                                {
                                    file.isDocument &&
                                    <RenderImageAndDocuments file={file} removeFile={removeFile} index={index}/>
                                }
                                {
                                    file.isCustomGpt &&
                                    <RenderAgent agentData={file} removeFile={removeFile} index={index}/>
                                }
                                {
                                    file.isPrompt &&
                                    <RenderPrompt promptData={file} removeFile={removeFile} index={index}/>
                                }
                                </React.Fragment>
                            ))
                        }
                    </>
                )}
            </div>
        </div>
    )
}

const UploadFileInput = ({ fileData, removeFile}: UploadFileInputProps) => {
    if (!fileData.length) return null;
    const hasAgent = Array.isArray(fileData) && fileData.some(file => file.isCustomGpt);
    const hasDocument = Array.isArray(fileData) && fileData.some(file => file.isDocument);
    const hasPrompt = Array.isArray(fileData) && fileData.some(file => file.isPrompt);
    const agentData = Array.isArray(fileData) && fileData.find(file => file.isCustomGpt);
    const promptData = Array.isArray(fileData) && fileData.find(file => file.isPrompt);
    if ((hasAgent && hasDocument) || (hasAgent && hasPrompt) || (hasPrompt && hasDocument)) {
        return <RenderAgentAndDocument fileData={fileData} removeFile={removeFile}/>
    }
    return (
        <div className="attached-files p-2">
            <div className="flex gap-2 flex-wrap">
                {Array.isArray(fileData) && !hasAgent && !hasPrompt ? (
                    fileData.map((file, index) => (
                        <React.Fragment key={file._id}>
                            <RenderImageAndDocuments file={file} removeFile={removeFile} index={index}/>
                        </React.Fragment>
                    ))
                ) : hasAgent ? (
                    <RenderAgent agentData={agentData} removeFile={removeFile} index={0}/>
                ) : (
                    <RenderPrompt promptData={promptData} removeFile={removeFile} index={0}/>
                )}
            </div>
        </div>
    );
};

export default UploadFileInput;
