import { DynamicImage } from '@/widgets/DynamicImage';
import React from 'react';

type RenderAIModalImageProps = {
    src: string;
    alt: string;
}

const RenderAIModalImage = ({ src, alt }: RenderAIModalImageProps) => {
    return (
        <div className='pt-0.5'>
            <div className='relative flex h-6 w-6 items-center justify-center overflow-hidden rounded-full'>
                <DynamicImage
                    src={src}
                    alt={alt}
                    loading="lazy"
                    width={40}
                    height={40}
                    className='rounded-sm'
                    placeholder = 'blur'
                />
            </div>
        </div>
    );
};

export default RenderAIModalImage;
