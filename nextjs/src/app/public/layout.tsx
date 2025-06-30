import '../../app/globals.css';
import ReduxProvider from '@/lib/ReduxProvider';

export const metadata = {
    title: 'Chat',
    description: 'Chat Page',
};

export default function RootLayout({ children }) {
    return (
        <ReduxProvider>
            <html lang="en">
                <body>{children}</body>
            </html>
        </ReduxProvider>
    );
}
