/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: false,
    // async headers() {
    //     return [
    //       {
    //         source: "/(.*)", // Apply CSP to all routes
    //         headers: [
    //           {
    //             key: "Content-Security-Policy",
    //             value: `
    //               script-src 'self' https://checkout.razorpay.com 'unsafe-inline';
    //               frame-src https://*.com;
    //             `.replace(/\s{2,}/g, " "), // Minify CSP value
    //           },
    //         ],
    //       },
    //     ];
    //   },
    async rewrites() {
        return [
            // {
            //     source: '/api/:path*',
            //     destination: `${process.env.NEXT_PUBLIC_DOMAIN_URL}/:path*`,
            // },
        ];
    },
    images: {
        remotePatterns: [
            {
                protocol: process.env.NEXT_PUBLIC_HTTPS_PROTOCOL,
                hostname: process.env.NEXT_PUBLIC_IMAGE_DOMAIN
            }
        ],
        domains: ['www.google.com','localhost'],
    },
    logging: {
        fetches: {
            fullUrl: true,
        }
    }
};

module.exports = nextConfig;
