import FileUploadIcon from '@/icons/FileUploadIcon';

type FileUploadProgressProps = {
    fileName: string;
    progress?: number;
    loading: boolean;
}

const FileUploadProgress = ({ fileName, progress, loading }: FileUploadProgressProps) => {
    return (
        <div className="w-full mt-3 border border-b10 rounded-large p-4">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <FileUploadIcon className="size-6" height={24} width={24} />
                    <h6 className="font-normal text-font-14">{fileName}</h6>
                </div>
                { loading && (<div className="text-font-14 font-bold text-[#2e047c]">{progress}%</div>) }
            </div>
            {
                loading && (
                    <div className="w-full h-[5px] bg-[#e8e0f8] rounded-lg mt-2">
                        <div
                            className="h-[5px] bg-[#2e047c] rounded-lg transition-all duration-500 ease-in-out"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                )
            }
        </div>
    );
};


export default FileUploadProgress;