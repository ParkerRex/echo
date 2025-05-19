import {
  HeadContent,
  Link,
  Outlet,
  Scripts,
  createRootRoute,
} from "@tanstack/react-router";
import { TanStackRouterDevtools } from "@tanstack/router-devtools";
import * as React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { DefaultCatchBoundary } from "../components/default-catch-boundary";
import { NotFound } from "../components/not-found";
// @ts-expect-error
import css from "../globals.css?url";
import { seo } from "../utils/seo";
import { useAuth } from "../hooks/useAuth";

// Create a single QueryClient instance for the app
const queryClient = new QueryClient();

export const Route = createRootRoute({
  head: () => ({
    meta: [
      {
        charSet: "utf-8",
      },
      {
        name: "viewport",
        content: "width=device-width, initial-scale=1",
      },
      ...seo({
        title:
          "TanStack Start | Type-Safe, Client-First, Full-Stack React Framework",
        description: `TanStack Start is a type-safe, client-first, full-stack React framework. `,
      }),
    ],
    links: [
      { rel: "stylesheet", href: css },
      {
        rel: "apple-touch-icon",
        sizes: "180x180",
        href: "/apple-touch-icon.png",
      },
      {
        rel: "icon",
        type: "image/png",
        sizes: "32x32",
        href: "/favicon-32x32.png",
      },
      {
        rel: "icon",
        type: "image/png",
        sizes: "16x16",
        href: "/favicon-16x16.png",
      },
      { rel: "manifest", href: "/site.webmanifest", color: "#fffff" },
      { rel: "icon", href: "/favicon.ico" },
    ],
  }),
  errorComponent: (props) => {
    return (
      <RootDocument>
        <DefaultCatchBoundary {...props} />
      </RootDocument>
    );
  },
  notFoundComponent: () => <NotFound />,
  component: RootComponent,
});

function RootComponent() {
  return (
    <RootDocument>
      <Outlet />
    </RootDocument>
  );
}

function RootDocument({ children }: { children: React.ReactNode }) {
  const { session, signOut, isLoading: authIsLoading } = useAuth();

  return (
    <html>
      <head>
        <HeadContent />
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <div className="p-2 flex flex-wrap sm:flex-nowrap gap-2 text-base sm:text-lg items-center">
            <Link
              to="/"
              activeProps={{
                className: "font-bold",
              }}
              activeOptions={{ exact: true }}
            >
              Home
            </Link>{" "}
            {authIsLoading ? (
              <span className="text-sm text-gray-500">Loading auth...</span>
            ) : session ? (
              <>
                <Link
                  to="/dashboard"
                  activeProps={{
                    className: "font-bold",
                  }}
                >
                  Dashboard
                </Link>{" "}
                <button
                  onClick={() => signOut()}
                  className="text-blue-600 hover:text-blue-800 text-base sm:text-lg"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to="/login"
                activeProps={{
                  className: "font-bold",
                }}
              >
                Login
              </Link>
            )}
          </div>
          <hr />
          {children}
          <TanStackRouterDevtools position="bottom-right" />
          <Scripts />
        </QueryClientProvider>
      </body>
    </html>
  );
}
