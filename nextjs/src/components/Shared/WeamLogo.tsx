import React from 'react';
import Image from 'next/image';
import WeamHorizontalLogo from '../../../public/weam-logo.svg';

const WeamLogo = ({ className, width, height }) => {
    return (
        <Image
            src={WeamHorizontalLogo}
            width={width}
            height={height}
            alt="Weam"
            className={className}
        />
    );
};

export default WeamLogo;
