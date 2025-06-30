import { AUTH, APP_ENVIRONMENT } from './config';

const ironOptions = {
    cookieName: AUTH.COOKIE_NAME,
    password: AUTH.COOKIE_PASSWORD,
    cookieOptions: {
        httpOnly: true,
        secure: APP_ENVIRONMENT === 'production',
    },
};

export default ironOptions;
