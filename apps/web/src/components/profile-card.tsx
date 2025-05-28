import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar"

interface ProfileCardProps {
  user?: {
    email?: string
    name?: string
    avatar?: string
  }
}

export function ProfileCard({ user }: ProfileCardProps) {
  const initials = user?.name
    ? user.name.split(' ').map(n => n[0]).join('').toUpperCase()
    : user?.email?.[0]?.toUpperCase() || 'U'

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <Avatar className="w-20 h-20">
            <AvatarImage src={user?.avatar} alt={user?.name || user?.email} />
            <AvatarFallback className="text-lg">{initials}</AvatarFallback>
          </Avatar>
        </div>
        <CardTitle>{user?.name || "User Profile"}</CardTitle>
        <CardDescription>{user?.email}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <h3 className="text-sm font-medium">Account Information</h3>
          <div className="text-sm text-gray-600">
            <p><strong>Email:</strong> {user?.email || "Not provided"}</p>
            <p><strong>Name:</strong> {user?.name || "Not provided"}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="flex-1">
            Edit Profile
          </Button>
          <Button variant="outline" className="flex-1">
            Settings
          </Button>
        </div>
      </CardContent>
    </Card>
  )
} 