import React from 'react';
import FileDropIcon from '@/icons/FileDropIcon';

type DrapDropUploaderProps = {
    isFileDragging: boolean;
};

const DrapDropUploader = ({ isFileDragging }: DrapDropUploaderProps) => {
    return (
        <div className="absolute w-full h-full">
            {isFileDragging && (
                <div className="absolute inset-0 bg-white bg-opacity-65 z-50 flex items-center justify-center pointer-events-none">
                    <div className="bg-white p-8 rounded-2xl text-center pointer-events-auto max-w-md w-full">
                        <div className="flex flex-col items-center gap-4">
                            <FileDropIcon className="w-10 h-10 text-black" />
                            <p className="text-xl font-bold text-black">
                                Upload Your Files Instantly
                            </p>
                            <p className="text-sm text-gray-600 leading-relaxed">
                                {
                                    `Drag and drop your files here, or click to upload 
                                    let's keep the conversation moving!`
                                }
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default React.memo(DrapDropUploader);
