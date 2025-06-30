import { getSession } from '@/config/withSession';
import { NextResponse } from 'next/server';

export async function POST(): Promise<NextResponse> {
    const session = await getSession();
    session.destroy();
    return NextResponse.json({ ok: true });
}
