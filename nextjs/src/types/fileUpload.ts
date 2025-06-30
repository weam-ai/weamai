export type FileUploadCustomType = {
    inputId: string;
    className?: string;
    placeholder?: string | React.ReactNode | any;
    placeholderClass?: string;
    onLoad?: (file: File) => void;
    prevImg?: string;
    page?: string;
    onLoadPreview?: (preview: string | ArrayBuffer | null) => void;
    showDescription?: boolean;
    setData?: (data: any) => void;
    allowedTypes?: readonly string[];
}