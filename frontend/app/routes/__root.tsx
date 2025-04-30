import {
    Outlet,
    HeadContent,
    Scripts,
    createRootRoute,
} from '@tanstack/react-router';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';
import appCss from '../styles/app.css?url';

export const Route = createRootRoute({
    head: () => ({
        meta: [
            {
                charSet: 'utf-8',
            },
            {
                name: 'viewport',
                content: 'width=device-width, initial-scale=1',
            },
            {
                title: 'automated marketing assistant',
            },
        ],
        links: [
            {
                rel: 'stylesheet',
                href: appCss,
            },
        ],
    }),

    component: () => (
        <RootDocument>
            <Outlet />
            <TanStackRouterDevtools />
        </RootDocument>
    ),
});

import { Link } from '@tanstack/react-router';

function RootDocument({ children }: { children: React.ReactNode }) {
    return (
        <html lang='en'>
            <head>
                <HeadContent />
            </head>
            <body>
                <div className='min-h-dvh flex flex-col'>
                    <nav style={{ padding: "1rem", background: "#f3f3f3", borderBottom: "1px solid #ddd" }}>
                        <Link to="/dashboard" style={{ marginRight: "1rem" }}>Dashboard</Link>
                        <Link to="/upload" style={{ marginRight: "1rem" }}>Upload</Link>
                        <Link to="/settings" style={{ marginRight: "1rem" }}>Settings</Link>
                        <Link to="/video/$videoId" params={{ videoId: "123" }} style={{ marginRight: "1rem" }}>Video 123</Link>
                    </nav>
                    <div className='flex-1'>{children}</div>
                </div>
                <Scripts />
            </body>
        </html>
    );
}
