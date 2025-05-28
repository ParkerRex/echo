import { createFileRoute, redirect } from "@tanstack/react-router"

export const Route = createFileRoute("/signup")({
  beforeLoad: async () => {
    // Redirect to the new Google OAuth login page
    throw redirect({ to: "/login" })
  },
})
