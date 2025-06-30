import '../../app/globals.css';
import { Toaster } from 'react-hot-toast';
import ReduxProvider from '@/lib/ReduxProvider';

export const viewport = {
  width: 'device-width',
  initialScale: 1.0,
  maximumScale: 1.0,
  userScalable: 'no',
};

export const metadata = {
    title: 'Weam',
    description: 'Weam',
};

export default function AuthLayout({ children }) {
    return (
        <ReduxProvider>
            <html lang="en">
                <body
                    suppressHydrationWarning={true}
                >
                    <Toaster position="top-right" reverseOrder={false} />
                    {children}
                </body>
            </html>
        </ReduxProvider>
    );
}
