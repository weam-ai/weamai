import React from 'react'
import { LINK } from '@/config/config';
import { DynamicImage } from '@/widgets/DynamicImage';

const ProfileImage = React.memo(({ user, classname, w, h, spanclass }) => {
    const profileImg = user?.profile?.uri;

    return (
        <>
            {profileImg !== undefined ? (
                <DynamicImage
                    src={`${LINK.AWS_S3_URL}${profileImg}`}
                    alt='user'
                    width={w}
                    height={h}
                    key={user.id}
                    className={classname}
                />
            ) : (
                <span className={spanclass}>
                    {user?.email?.charAt(0)?.toUpperCase()}
                </span>
            )}
        </>
    );
})

export default ProfileImage;

const getRandomColor = () => {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
};