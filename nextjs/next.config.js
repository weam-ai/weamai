/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: false,
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
                protocol: process.env.NEXT_PUBLIC_HTTPS_PROTOCOL || 'https',  // Default to 'https' if not set
                hostname: process.env.NEXT_PUBLIC_IMAGE_DOMAIN || 'default.cdn.com' // Default domain if not set
            }
        ],
        domains: ['www.google.com', 'localhost'], // Add any other domains you expect images from
    },
    logging: {
        fetches: {
            fullUrl: true,
        }
    }
};

module.exports = nextConfig;
