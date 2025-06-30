import React from 'react'
import {
    Dialog,
    DialogContent,
    DialogTrigger,
} from '@/components/ui/dialog';
import Image from 'next/image';
import DownloadIcon from '@/icons/DownloadIcon';
import { DynamicImage } from '@/widgets/DynamicImage';

const PreviewImage = ({className="",src,actualWidth,actualHeight,previewWidth,previewHeight}) => {
  return (
    <Dialog>
    <div className={`relative overflow-hidden rounded-10 group ${className}`}>
        
        <DialogTrigger className=''>
            <DynamicImage 
                src={src} 
                alt={src} 
                width={actualWidth} 
                height={actualHeight}
                className="object-cover rounded-10 transition duration-300 ease-in-out group-hover:brightness-75"
                placeholder='blur'
            />
        </DialogTrigger>
        <a
            href={src}
            download
            className="absolute top-2 right-2 opacity-0 transition-opacity duration-300 group-hover:opacity-100 bg-white rounded-md z-10"
        >
            <DownloadIcon
                width={30}
                height={30}
                className="cursor-pointer text-gray-400 fill-b4"
                showBorder={false}
            />
        </a>

    </div>

    <DialogContent className="container bg-black text-white w-full max-w-[600px] p-0 border-none">
        <div className="flex justify-center items-center relative group">
            <Image
                src={src}
                width={previewWidth}
                height={previewHeight}
                priority
                className="rounded-10 transition duration-300 ease-in-out my-7 w-full h-full object-cover"
                alt="image"
            />

            <a
                href={src}
                download
                className="absolute opacity-0 group-hover:opacity-100 left-[calc(50%-20px)] top-[50%] flex items-center justify-center translate-y-[-50%] text-white rounded-full w-[50px] h-[50px] bg-white transition ease-in-out duration-300"
            >
                <DownloadIcon
                    width={40}
                    height={40}
                    className="text-gray-400 fill-b4"
                    showBorder={false}
                />
            </a>
        </div>
    </DialogContent>
    </Dialog>
  )
}

export default PreviewImage