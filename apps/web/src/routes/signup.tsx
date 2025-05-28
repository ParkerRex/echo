import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/signup")({
  beforeLoad: async ({ context }) => {
    if (context.authState.isAuthenticated) {
      throw redirect({ to: "/" })
    }
    // Redirect to the new Google OAuth login page
    throw redirect({ to: "/login" })
  },
})
