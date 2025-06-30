import Image from 'next/image';
import React from 'react';
import {
    Carousel,
    CarouselContent,
    CarouselItem,
    CarouselNext,
    CarouselPrevious,
} from '@/components/ui/carousel';
import { WEB_RESOURCES_DATA } from '@/utils/constant';

const ShowResources = React.memo(({ response }) => {
    const resources = response?.[WEB_RESOURCES_DATA];
    return (
        <div className="py-6">
            <Carousel
                opts={{
                    align: 'start',
                }}
                className="w-full max-md:pr-5"
            >
                <CarouselContent className="m-0 items-center px-4">
                    {Array.isArray(resources) &&
                        resources.map((item, idx) => (
                            <CarouselItem
                                className="flex-none max-md:basis-1/2 border px-4 py-2 mr-1 rounded-lg"
                                key={`${item?.original_url}-${idx}`}
                            >
                                <a
                                    href={item?.original_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center justify-center gap-x-2 hover:underline font-semibold text-font-12 text-gray-600"
                                >
                                    <Image
                                        src={item?.logo_url || '/globe.png'}
                                        alt={item?.domain}
                                        width={30}
                                        height={30}
                                        className="w-5 h-auto"
                                        onError={(e) => {
                                            e.currentTarget.src = '/globe.png';
                                        }}
                                    />
                                    {item?.domain}
                                </a>
                            </CarouselItem>
                        ))}
                </CarouselContent>
                {Array.isArray(resources) && resources.length > 5 && (
                    <>
                        <CarouselPrevious />
                        <CarouselNext className="max-md:right-[-12px]" />
                    </>
                )}
            </Carousel>
        </div>
    );
});

ShowResources.displayName = 'ShowResources';

export default ShowResources;
