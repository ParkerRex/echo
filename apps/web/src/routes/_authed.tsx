import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"
import type { ErrorComponentProps } from "@tanstack/react-router"
import { DefaultCatchBoundary } from "src/components/default-catch-boundary"

/**
 * Loading component for authenticated routes
 */
function AuthedLayoutPendingComponent() {
  return (
    <div className="flex items-center justify-center h-screen">
      <svg
        className="animate-spin h-10 w-10 text-primary"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span className="ml-3 text-xl">Authenticating...</span>
    </div>
  )
}

/**
 * Error component for authentication and other errors in authenticated routes
 */
function AuthedLayoutErrorComponent({ error }: ErrorComponentProps) {
  return <DefaultCatchBoundary error={error} />
}

export const Route = createFileRoute("/_authed")({
  beforeLoad: ({ context, location }) => {
    // Use the user from root context (consistent between server and client)
    if (!context.user) {
      // User is not authenticated, redirect to login with return URL
      throw redirect({
        to: "/login",
        search: {
          redirect: encodeURIComponent(location.pathname + location.search)
        },
      })
    }

    // User is authenticated, pass through context
    return {
      user: context.user,
    }
  },
  component: AuthedLayoutComponent,
  pendingComponent: AuthedLayoutPendingComponent,
  errorComponent: AuthedLayoutErrorComponent,
})

/**
 * Authenticated layout component
 * Only renders when user is authenticated (guaranteed by beforeLoad middleware)
 */
function AuthedLayoutComponent() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Optional: Add authenticated navigation bar */}
      {/* <AuthenticatedNavbar /> */}

      {/* Main content area */}
      <main className="container mx-auto px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}
