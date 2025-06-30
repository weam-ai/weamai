import { getSession } from '@/config/withSession';
import { NextResponse } from 'next/server';

export async function POST (res: Request): Promise<NextResponse> {
    const response = await res.json()
    const session = await getSession();
    session.user.access_token = response.access_token
    await session.save();
    return NextResponse.json({ ok: true });
}