'use client';
import { useEffect } from 'react';

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {

    useEffect(() => {
        console.error('Global Error', error);
    }, [error]);

    return (
        // global-error must include html and body tags
        <html>
            <body className="min-h-screen flex flex-col items-center justify-center">
                <h2 className="text-2xl font-bold mb-4">Something went wrong!</h2>
                <p className="text-gray-600 mb-6">Our team has been notified and will fix this issue as soon as possible.</p>
                <a
                    href="/"
                    className="bg-blue text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-primary-dark transition"
                >
                    Go Home
                </a>
            </body>
        </html>
    );
}