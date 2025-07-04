'use client';
import React, { useState } from 'react';
import Image from 'next/image';
import RemoveIcon from '@/icons/RemoveIcon';
import { FILE, PROFILE_IMG_SIZE_MESSAGE, FILE_SIZE_MESSAGE, IMAGE_ALLOWED_TYPES } from '@/utils/constant';
import Toast from '@/utils/toast';
import { FileUploadCustomType } from '@/types/fileUpload';


/**
 * 
 * @param placeholder pass image when actual image is removed then placeholder image will be shown 
 * @returns 
 */
const FileUploadCustom = ({
    inputId,
    className,
    placeholder,
    placeholderClass,
    onLoad,
    prevImg,
    page,
    onLoadPreview,
    showDescription = false,
    setData,
    allowedTypes = IMAGE_ALLOWED_TYPES
}: FileUploadCustomType) => {
    // Upload image start
    const [uploadedImg, setUploadedImg] = useState(prevImg);
    const [showRemoveButton, setShowRemoveButton] = useState(
        prevImg ? true : false
    );

    const handleUpload = (e) => {
        const file = e.target.files[0];
    
        if (!allowedTypes.includes(file.type)) {
            Toast('Please upload a valid image file (JPG,JPEG, PNG, GIF)', 'error');
            return false;
        }
        
        if (file.size > 500000 && (page == 'profile' || page == 'agent')) {
            Toast(PROFILE_IMG_SIZE_MESSAGE, 'error');
            return false;
        } else if (file.size > FILE.SIZE) {
            Toast(FILE_SIZE_MESSAGE, 'error');
            return false;
        }

        const reader = new FileReader();

        reader.onloadend = () => {
            setUploadedImg(reader.result);
            onLoadPreview(reader.result);
            setShowRemoveButton(true);
        };

        if (file) {
            reader.readAsDataURL(file);
            onLoad(file);
        }
    };

    const handleRemove = () => {
        setUploadedImg(null);
        setShowRemoveButton(false);
        onLoad(null);
        onLoadPreview(null);
        setData(prev => ({ ...prev, removeCoverImg: true }));
    };
    // Upload image end

    return (
        <div className={`upload-img flex items-center ${className}`}>
            <div className="placeholder-wrap relative">
                {uploadedImg ? (
                    <div className="uploaded-img flex items-center justify-center w-[50px] h-[50px] min-w-[50px] rounded-full bg-b11 mr-2.5">
                        <Image
                            src={uploadedImg}
                            alt="uploaded img"
                            height={50}
                            width={50}
                            className="h-[50px] w-[50px] object-cover rounded-full"
                        />
                    </div>
                ) : (
                    <div className="placeholder-img flex items-center justify-center w-[50px] h-[50px] min-w-[50px] rounded-full bg-b11 mr-2.5">
                        <Image
                            src={placeholder}
                            alt="workspace placeholder"
                            className={`${placeholderClass} object-contain`}
                        />
                    </div>
                )}
                {showRemoveButton && (
                    <div
                        className="remove-button-btn cursor-pointer absolute -bottom-2 left-[15px] flex items-center justify-center bg-white w-5 h-5 rounded-full shadow-3 p-0.5 "
                        onClick={handleRemove}
                    >
                        <RemoveIcon
                            width={15}
                            height={17}
                            className="fill-b7 h-4 w-4 object-contain"
                        />
                    </div>
                )}
            </div>
            <input
                type="file"
                onChange={handleUpload}
                style={{ display: 'none' }}
                id={inputId}
                accept="image/*"
                value={''}
            />
            <label
                htmlFor={inputId}
                className="text-font-14 font-semibold text-b2 cursor-pointer"
            >
                Upload Image
                {showDescription && <span className='block font-normal text-font-12 text-b5'>Keep your profile picture under 500 kb</span>}
            </label>
        </div>
    );
};

export default FileUploadCustom;