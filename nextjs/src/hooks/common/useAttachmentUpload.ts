import { useRef, useState } from 'react';
import Toast from '@/utils/toast';
import { MODULE_ACTIONS } from '@/utils/constant';
import commonApi from '@/api';

const useAttachmentUpload = () => {
    const [fileLoader, setFileLoader] = useState(false);
    const [uploadedFiles, setUploadedFiles] = useState([]);
    const [isFileUploading, setIsFileUploading] = useState(false);
    const fileInputRef = useRef(null);

    const uploadMedia = async (files) => {
        try {
            const formData = new FormData();
            files.forEach((file, index) => {
                formData.append(`attachment`, file);
            });
            const response = await commonApi({
                action: MODULE_ACTIONS.ALL_MEDIA_UPLOAD,
                config: {
                    'Content-Type': 'multipart/form-data'
                },
                data: formData
            })
            return response.data;
        } catch (error) {
            console.log('error: ', error);
        }
    };

    const removeMedia = async (key) => {
        try {
            const response = await commonApi({
                action: MODULE_ACTIONS.DELETE_S3_MEDIA,
                data: {
                    key
                }
            })
            return response.data;
        } catch (error) {
            console.log('error: ', error);
        }
    };

    const handleFileChange = async (event) => {
        setIsFileUploading(true);
        const files = event.target.files;
        const fileList = Array.from(files);
        if(fileList.length > 5){
            Toast('Only 5 files allowed', 'error');
            return;
        }
        const enhancedFiles = fileList.map((file,index) => ({
            file: file,
            index,
            uploaded: false
        }));
        setUploadedFiles(enhancedFiles);

        const uploadedFiles = await uploadMedia(fileList);

        setUploadedFiles(prev=>{
            let updateItems = [...prev];
            updateItems = updateItems.map((item, index) => ({ ...item, uploaded: true, meta_data: uploadedFiles[index] }))
            return updateItems;
        })
        setIsFileUploading(false);
    };

    const resetMediaUpload = () => {
        setIsFileUploading(false);
        setUploadedFiles([]);
        if(fileInputRef.current){
            fileInputRef.current.value = null;
        }
    }

    const removeUploadedFile = async (item) => {
        if (item?.meta_data?.uri) {
            // await removeMedia(item.meta_data.uri); // TODO : Fix backend side api
            setUploadedFiles(prev => {
                let updateItems = [...prev];
                updateItems = updateItems.filter(media => media.meta_data.uri != item.meta_data.uri);
                return updateItems;
            })
        }
    };

    return {
        fileLoader,
        handleFileChange,
        uploadedFiles,
        setUploadedFiles,
        fileInputRef,
        isFileUploading,
        resetMediaUpload,
        removeUploadedFile
    }
};

export default useAttachmentUpload;
