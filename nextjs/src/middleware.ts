import { NextRequest, NextResponse } from 'next/server';
import { LINK, AUTH } from './config/config';
import { encryptedData } from './utils/helper';

const CSRF_API_URL = `${LINK.COMMON_NODE_API_URL}/v1/csrf`;
const CSRF_PASSWORD = AUTH.CSRF_TOKEN_SECRET || 'secret';
const COOKIE_EXPIRE_SECONDS = 60 * 60;

export async function middleware(req: NextRequest) {
    // Temporarily disable CSRF for development
    return NextResponse.next();
    
    // Original CSRF logic (commented out)
    
    const csrfCookie = req.cookies.get(AUTH.CSRF_COOKIE_NAME);
    if (csrfCookie?.value) {
        return NextResponse.next();
    }

    const response = await fetch(CSRF_API_URL, {
        method: 'GET',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': `Bearer ${CSRF_PASSWORD}`,
        }
    });

    if (!response.ok) {
        console.error('Failed to fetch CSRF token from backend');
        return NextResponse.next();
    }

    const data = await response.json();
    const csrfToken = encryptedData(data?.csrfToken);
    const csrfTokenRaw = encryptedData(data?.cookie);

    if (!csrfToken || !csrfTokenRaw) {
        console.error('Invalid CSRF response');
        return NextResponse.next();
    }

    const res = NextResponse.next();
    res.cookies.set(AUTH.CSRF_COOKIE_NAME, csrfToken, {
        httpOnly: false,
        secure: true,
        sameSite: 'strict',
        path: '/',
    });
    res.cookies.set(AUTH.CSRF_COOKIE_RAW_NAME, csrfTokenRaw, {
        httpOnly: false,
        secure: true,
        sameSite: 'strict',
        path: '/',
    });
    return res;
}

export const config = {
    matcher: ['/((?!api|_next|static|favicon.ico).*)'],
};
