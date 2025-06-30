import { getSession } from '@/config/withSession';
import { NextResponse } from 'next/server';

export async function POST(req: Request): Promise<NextResponse> {
    const [response, session] = await Promise.all([req.json(), getSession()]);
    session.user = response;
    await session.save();
    return NextResponse.json({ ok: true });
}