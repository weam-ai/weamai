// Fix import for NextRequest and NextResponse
import type { NextRequest } from 'next/server';
import { NextResponse } from 'next/server';
import { getSession } from '@/config/withSession';
import { API_URL, NODEJS_API_URL } from '@/config/config';

export async function POST(req: NextRequest) {
  try {
    const session = await getSession();
    
    if (!session?.user?.access_token) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Try both API endpoints to ensure compatibility
    const apiUrl = NODEJS_API_URL || API_URL;
    console.log('jwt token', `jwt ${session.user.access_token}`)
    // const response = await fetch(`${apiUrl}/napi/v1/web/auth/complete-onboarding`, {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //     'Authorization': `jwt ${session.user.access_token}`
    //   },
    //   body: JSON.stringify({
    //     onboard: false
    //   })
    // });


    // if (!response.ok) {
    //   const errorData = await response.json();
    //   return NextResponse.json(
    //     { error: errorData.message || 'Failed to complete onboarding' },
    //     { status: response.status }
    //   );
    // }

    // const data = await response.json();
    
    // Update the session to set onboard to false
    if (session.user) {
      session.user.onboard = false;
      await session.save();
    }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in complete-onboarding API route:', error);
    return NextResponse.json(
      { error: 'Internal Server Error' },
      { status: 500 }
    );
  }
}