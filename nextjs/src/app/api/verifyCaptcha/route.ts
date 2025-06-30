import { RECAPTCHA } from '@/config/config';

const VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify";
const SECRET_KEYS = {
  v2: RECAPTCHA.SECRET_KEY_V2,
  v3: RECAPTCHA.SECRET_KEY_V3,
};

export async function POST(req) {
  try {
    const { token, version } = await req.json();

    if (!token) {
      return new Response(
        JSON.stringify({ success: false, message: "No CAPTCHA token provided." }),
        { status: 400 }
      );
    }

    const secretKey = SECRET_KEYS[version];
    if (!secretKey) {
      return new Response(
        JSON.stringify({ success: false, message: "Invalid or missing reCAPTCHA version." }),
        { status: 400 }
      );
    }

    const response = await fetch(VERIFY_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        secret: secretKey,
        response: token,
      }),
    });

    const data = await response.json();
    const success = data.success || false;
    // v3 returns 'score'; v2 does not
    const score = data.score ?? 1; 

    // If verification failed or v3 score is below threshold
    if (!success || (version === 'v3' && score < 0.5)) {
      return new Response(
        JSON.stringify({
          success: false,
          score,
          message: "reCAPTCHA verification failed or score below threshold.",
        }),
        { status: 200 }
      );
    }

    return new Response(
      JSON.stringify({
        success: true,
        score,
        message: "CAPTCHA verified successfully.",
      }),
      { status: 200 }
    );
  } catch (error) {
    console.error("Error verifying CAPTCHA:", error.message);
    return new Response(
      JSON.stringify({ success: false, message: "Internal server error." }),
      { status: 500 }
    );
  }
}
