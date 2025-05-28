import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import type { ErrorComponentProps } from "@tanstack/react-router";
import { supabase } from "@echo/db/clients";
import { DefaultCatchBoundary } from "src/components/default-catch-boundary";
import React from "react";

// Define a simple loading component to be used as the pendingComponent
function AuthedLayoutPendingComponent() {
	return (
		<div className="flex items-center justify-center h-screen">
			<svg className="animate-spin h-10 w-10 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
				<circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
				<path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
			</svg>
			<span className="ml-3 text-xl">Loading authenticated session...</span>
		</div>
	);
}

// Error component for non-auth errors in authenticated routes
function AuthedLayoutErrorComponent({ error }: ErrorComponentProps) {
	return <DefaultCatchBoundary error={error} />;
}

export const Route = createFileRoute("/_authed")({
	beforeLoad: async ({ location }) => {
		const { data: { session }, error } = await supabase().auth.getSession();

		if (error) {
			console.error("Error getting session in _authed beforeLoad:", error);
			// Handle error appropriately, perhaps redirect to an error page or login
			throw redirect({
				to: "/login",
				search: {
					redirect: location.pathname, // Pass the original intended path
				},
			});
		}

		if (!session) {
			throw redirect({
				to: "/login",
				search: {
					// Store the attempted URL to redirect back after login
					redirect: location.pathname,
				},
			});
		}
		// If session exists, proceed to load the route component.
		// Optionally, you can pass user/session to context if needed by child routes directly from loader
		// return { user: session.user }; // Example: if you want to put user in context
		return {}; // Or an empty object if not passing anything specific to context here
	},
	component: AuthedLayoutComponent,
	pendingComponent: AuthedLayoutPendingComponent,
	errorComponent: AuthedLayoutErrorComponent,
	// Auth failures are handled by redirects in beforeLoad.
	// Non-auth errors are handled by the errorComponent above.
});

function AuthedLayoutComponent() {
	// This component will render if beforeLoad successfully finds a session.
	// It should provide the Outlet for nested authenticated routes.
	// You could also include a shared layout for authenticated pages here (e.g., a navbar with user info).
	// const { user } = Route.useRouteContext(); // Example if context was populated in beforeLoad

	// For now, a simple Outlet.
	// Components within this layout can use the useAuth() hook to get user/session details.
	return (
		<>
			{/* Example: <AuthenticatedNavbar /> */}
			<Outlet />
		</>
	);
}
