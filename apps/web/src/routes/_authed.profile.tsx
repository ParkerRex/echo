import { createFileRoute } from "@tanstack/react-router"
import { ProfileCard } from "src/components/profile-card"
import { useAuth } from "src/lib/useAuth"

export const Route = createFileRoute("/_authed/profile")({
  component: RouteComponent,
})

function RouteComponent() {
  const { user } = useAuth()

  const profileUser = user ? {
    email: user.email,
    name: user.user_metadata?.full_name || user.email?.split('@')[0],
    avatar: user.user_metadata?.avatar_url
  } : undefined

  return <ProfileCard user={profileUser} />
}
