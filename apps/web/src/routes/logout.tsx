import { createFileRoute, redirect } from "@tanstack/react-router"
import { signOut } from "src/services/auth.api"

/**
 * Logout route that immediately signs out the user and redirects
 * Uses our hardened server-side authentication system
 */
export const Route = createFileRoute("/logout")({
  preload: false,
  loader: async () => {
    try {
      // Use our hardened signOut server function
      await signOut()

      // Redirect to home page after successful logout
      throw redirect({
        to: "/",
        replace: true,
      })
    } catch (error) {
      console.error("Logout error:", error)

      // Even if logout fails, redirect to home page
      // This ensures users don't get stuck on the logout page
      throw redirect({
        to: "/",
        replace: true,
      })
    }
  },
})
