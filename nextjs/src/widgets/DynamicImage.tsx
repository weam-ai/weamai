import Image, { ImageProps } from 'next/image';

export const DynamicImage: React.FC<ImageProps> = ({
    src,
    alt,
    className,
    width,
    height,
    placeholder,
    blurDataURL = 'data:image/svg+xml;base64,CiAgICA8c3ZnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Zycgdmlld0JveD0nMCAwIDggNSc+CiAgICAgIDxmaWx0ZXIgaWQ9J2InIGNvbG9yLWludGVycG9sYXRpb24tZmlsdGVycz0nc1JHQic+CiAgICAgICAgPGZlR2F1c3NpYW5CbHVyIHN0ZERldmlhdGlvbj0nMScgLz4KICAgICAgPC9maWx0ZXI+CgogICAgICA8aW1hZ2UgcHJlc2VydmVBc3BlY3RSYXRpbz0nbm9uZScgZmlsdGVyPSd1cmwoI2IpJyB4PScwJyB5PScwJyBoZWlnaHQ9JzEwMCUnIHdpZHRoPScxMDAlJyAKICAgICAgaHJlZj0nZGF0YTppbWFnZS9hdmlmO2Jhc2U2NCwvOWovMndCREFBZ0dCZ2NHQlFnSEJ3Y0pDUWdLREJRTkRBc0xEQmtTRXc4VUhSb2ZIaDBhSEJ3Z0pDNG5JQ0lzSXh3Y0tEY3BMREF4TkRRMEh5YzVQVGd5UEM0ek5ETC8yd0JEQVFrSkNRd0xEQmdORFJneUlSd2hNakl5TWpJeU1qSXlNakl5TWpJeU1qSXlNakl5TWpJeU1qSXlNakl5TWpJeU1qSXlNakl5TWpJeU1qSXlNakl5TWpML3dBQVJDQUFMQUJBREFTSUFBaEVCQXhFQi84UUFGZ0FCQVFFQUFBQUFBQUFBQUFBQUFBQUFBd1VHLzhRQUp4QUFBUU1EQWdRSEFBQUFBQUFBQUFBQUFRSURCQUFGRVJJaEJqR0JrU0pCUW1GeHNjSC94QUFWQVFFQkFBQUFBQUFBQUFBQUFBQUFBQUFDQlAvRUFCb1JBQUlEQVFFQUFBQUFBQUFBQUFBQUFBRUNBQU1TRVVILzJnQU1Bd0VBQWhFREVRQS9BRGY0c3VFaTlQQnRoeFVVZ0JLRUhJV0FkMUU0MkFCNWVaeDgxRG5JY3ZVbTVMaXpFTnBqeHdzdHVNbENuTUhKQTY4OC9WWnVUY1pyVDdMS0pUb2FXZ2FrYWlVN2UzVTk2Uis0VEE2RkprdUpPdzhLc2VuSDZlOUhJTnZXbFNKbXM1OW4vOWs9JyAvPgogICAgPC9zdmc+CiAg',
    sizes = '(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw',
}) => {
    // Validate src prop
    if (!src) {
        console.warn('DynamicImage: src prop is required but was not provided');
        return null;
    }

    return (
        <Image
            src={src}
            alt={alt || 'Image'}
            className={className}
            width={width}
            height={height}
            placeholder={placeholder}
            blurDataURL={blurDataURL}
            sizes={sizes}
        />
    );
};
